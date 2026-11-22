local ns = select(2, ...) ---@class MiniLootNS

local db = ns.Settings.db
local MiniLootMessageGroup = ns.Messages.MiniLootMessageGroup
local MessagesCollection = ns.Messages.MessagesCollection
local ProcessChatMessage = ns.Messages.ProcessChatMessage
local EvaluateFilters = ns.Filters.EvaluateFilters
local TableContains = ns.Utils.TableContains

local AddMessageEventFilter = ChatFrame_AddMessageEventFilter or ChatFrameUtil.AddMessageEventFilter ---@type fun(event: WowEvent, callback: fun())
local RemoveMessageEventFilter = ChatFrame_RemoveMessageEventFilter or ChatFrameUtil.RemoveMessageEventFilter  ---@type fun(event: WowEvent, callback: fun())

local PendingSelfRolls = {}
local LootRollLinks = {}
local PENDING_SELF_ROLL_TTL = 90
local RollTypeToResultType = {
    [0] = "YouPass",
    [1] = "YouNeed",
    [2] = "YouGreed",
    [3] = "YouDisenchant",
    [4] = "YouTransmog",
}

local SyntheticSelfRollMessage = {
    group = MiniLootMessageGroup.LootRollYouDecide,
    events = { "CHAT_MSG_LOOT" },
    formats = {},
    defaultDebounce = 0,
}

local rollOnLootHooked = false
local confirmLootRollHooked = false
local syntheticResultHandler = nil
local suppressRawTransmogMessages = 0
local suppressRawTransmogUntil = 0

---@param value any
---@return boolean
local function IsSafeValue(value)
    return type(issecretvalue) ~= "function" or not issecretvalue(value)
end

---@param rollID number
---@return string?
local function GetCachedLootRollLink(rollID)
    local link = LootRollLinks[rollID]
    if link then
        return link
    end
    if type(GetLootRollItemLink) ~= "function" then
        return
    end
    link = GetLootRollItemLink(rollID)
    if type(link) ~= "string" or link == "" or not IsSafeValue(link) then
        return
    end
    LootRollLinks[rollID] = link
    return link
end

---@param rollID number
local function RemovePendingSelfRollByID(rollID)
    for i = #PendingSelfRolls, 1, -1 do
        if PendingSelfRolls[i].rollID == rollID then
            table.remove(PendingSelfRolls, i)
        end
    end
end

local function PrunePendingSelfRolls()
    local now = GetTime()
    for i = #PendingSelfRolls, 1, -1 do
        if now - PendingSelfRolls[i].time > PENDING_SELF_ROLL_TTL then
            table.remove(PendingSelfRolls, i)
        end
    end
end

local function CanOutputSyntheticResult(result, message)
    if not db.Enabled then
        return false
    end
    local group = message.group
    if db.EnabledGroups[group] == false then
        return false
    end
    if db.IgnoredGroups[group] or message.group == MiniLootMessageGroup.Ignore then
        return false
    end
    return not EvaluateFilters(db.Filters, result, message)
end

---@param rollID number
local function EmitPendingTransmogRoll(rollID)
    for i, pending in ipairs(PendingSelfRolls) do
        if pending.rollID == rollID and pending.Type == "YouTransmog" then
            local link = pending.Link or GetCachedLootRollLink(rollID)
            if not link then
                return
            end
            table.remove(PendingSelfRolls, i)
            local result = {
                Type = "YouTransmog",
                Link = link,
            }
            if syntheticResultHandler and CanOutputSyntheticResult(result, SyntheticSelfRollMessage) then
                syntheticResultHandler(result, SyntheticSelfRollMessage)
                suppressRawTransmogMessages = suppressRawTransmogMessages + 1
                suppressRawTransmogUntil = GetTime() + 2
            end
            return
        end
    end
end

---@param rollID number
---@param rollType number
local function CacheSelfRoll(rollID, rollType)
    local resultType = RollTypeToResultType[rollType]
    if not resultType or type(rollID) ~= "number" then
        return
    end
    RemovePendingSelfRollByID(rollID)
    PendingSelfRolls[#PendingSelfRolls + 1] = {
        rollID = rollID,
        Type = resultType,
        Link = GetCachedLootRollLink(rollID),
        time = GetTime(),
    }

    -- Unlike Need/Greed/Pass, Retail does not provide a reliable self-chat
    -- format for Transmog. Emit it from the actual roll action instead. The
    -- short delay gives CONFIRM_LOOT_ROLL time to remove the provisional
    -- entry for bind-on-pickup items; ConfirmLootRoll will then cache it again
    -- only after the player accepts the confirmation.
    if resultType == "YouTransmog" and C_Timer and C_Timer.After then
        C_Timer.After(0.1, function()
            EmitPendingTransmogRoll(rollID)
        end)
    end
end

local function EnsureLootRollHook()
    if type(hooksecurefunc) ~= "function" then
        return
    end
    if not rollOnLootHooked and type(RollOnLoot) == "function" then
        hooksecurefunc("RollOnLoot", CacheSelfRoll)
        rollOnLootHooked = true
    end
    if not confirmLootRollHooked and type(ConfirmLootRoll) == "function" then
        hooksecurefunc("ConfirmLootRoll", CacheSelfRoll)
        confirmLootRollHooked = true
    end
end

---@param text string
---@return number?
local function GetLootHistoryIDFromText(text)
    if type(text) ~= "string" or not IsSafeValue(text) then
        return
    end
    local linkedID = text:match("|HlootHistory:(%d+)|h")
    if linkedID then
        return tonumber(linkedID)
    end
    if #text == 0 or #text > 4 or text:find("|", 1, true) then
        return
    end
    local value = 0
    local multiplier = 1
    for i = 1, #text do
        value = value + text:byte(i) * multiplier
        multiplier = multiplier * 256
    end
    return value
end

---@param text string
---@param link string
---@return boolean
local function TextContainsLootLink(text, link)
    if text:find(link, 1, true) then
        return true
    end
    local hyperlink = link:match("|H([^|]+)|h")
    return hyperlink ~= nil and text:find("|H" .. hyperlink .. "|h", 1, true) ~= nil
end

---@param text string
---@param transmogOnly boolean
---@param preview boolean
---@return table?, number?
local function FindPendingSelfRoll(text, transmogOnly, preview)
    if not preview then
        PrunePendingSelfRolls()
    end
    local now = GetTime()
    for i, pending in ipairs(PendingSelfRolls) do
        if now - pending.time <= PENDING_SELF_ROLL_TTL and
            (not transmogOnly or pending.Type == "YouTransmog") and
            (transmogOnly or (pending.Link and TextContainsLootLink(text, pending.Link))) then
            return pending, i
        end
    end
end

---@param event WowEvent
---@param text string
---@param preview boolean
---@return MiniLootMessageFormatSimpleParserResults?, MiniLootMessage?
local function ProcessPendingSelfRoll(event, text, preview)
    if event ~= "CHAT_MSG_LOOT" or type(text) ~= "string" or not IsSafeValue(text) then
        return
    end
    local lootHistoryID = GetLootHistoryIDFromText(text)
    if not lootHistoryID then
        return
    end

    -- Transmog has no LOOT_ROLL_*_SELF GlobalString. The client currently emits
    -- the loot-history ID as a tiny raw string, so pair it with the oldest
    -- pending Transmog click instead of assuming that ID is the rollID.
    local isRawLootHistoryID = #text <= 4 and not text:find("|", 1, true)
    local pending, index = FindPendingSelfRoll(text, isRawLootHistoryID, preview)
    if not pending then
        return
    end
    if not preview then
        table.remove(PendingSelfRolls, index)
    end

    local link = pending.Link or LootRollLinks[pending.rollID]
    if not link and not preview then
        link = GetCachedLootRollLink(pending.rollID)
    end
    if not link then
        return
    end
    return {
        Type = pending.Type,
        Link = link,
        LootHistory = lootHistoryID,
    }, SyntheticSelfRollMessage
end

---@param result MiniLootMessageFormatSimpleParserResults?
---@param message MiniLootMessage?
local function ClearPendingSelfRoll(result, message)
    if not result or not message or message.group ~= MiniLootMessageGroup.LootRollYouDecide then
        return
    end
    for i = #PendingSelfRolls, 1, -1 do
        local pending = PendingSelfRolls[i]
        if pending.Type == result.Type and (not pending.Link or not result.Link or pending.Link == result.Link) then
            table.remove(PendingSelfRolls, i)
            return
        end
    end
end

---@type MiniLootNSEventCallbackResult
local ProcessChatEvent

-- Key verified policies by "<interface>:<build>". Add an entry only with a
-- client trace that establishes whether quest XP is reported natively.
---@type table<string, "native"|"turn-in">
local questExperienceSourceByBuild = {}
local questExperienceMessage = { group = MiniLootMessageGroup.Experience }

local function GetQuestExperienceSource()
    local _, build, _, interface = GetBuildInfo()
    if build and interface then
        return questExperienceSourceByBuild[interface .. ":" .. build]
    end
end

local useQuestTurnInExperience = GetQuestExperienceSource() ~= "native"

local function RecordQuestExperience(xp)
    local result = { Type = "Experience", Value = xp }
    if syntheticResultHandler and CanOutputSyntheticResult(result, questExperienceMessage) then
        syntheticResultHandler(result, questExperienceMessage)
    end
end

---@type table<WowEvent, MiniLootNSEventCallbackResult>
local EventHandlers = {
    START_LOOT_ROLL = function(event, rollID)
        if type(rollID) == "number" then
            GetCachedLootRollLink(rollID)
        end
    end,
    CONFIRM_LOOT_ROLL = function(event, rollID)
        if type(rollID) == "number" then
            RemovePendingSelfRollByID(rollID)
        end
    end,
    CANCEL_ALL_LOOT_ROLLS = function()
        table.wipe(PendingSelfRolls)
        table.wipe(LootRollLinks)
    end,
    QUEST_TURNED_IN = function(event, ...)
        ---@type number?, number?, number?
        local questID, xp, money = ...
        if useQuestTurnInExperience and type(xp) == "number" and IsSafeValue(xp) and xp > 0 then
            RecordQuestExperience(xp)
        end
        local coinText = C_CurrencyInfo and C_CurrencyInfo.GetCoinText or GetCoinText
        if money and money > 0 and coinText and type(YOU_LOOT_MONEY) == "string" then
            return ProcessChatEvent("CHAT_MSG_MONEY", format(YOU_LOOT_MONEY, coinText(money)))
        end
    end,
}

local function GetMessageEvents()
    local events = {} ---@type WowEvent[]
    local numEvents = #events
    for _, message in ipairs(MessagesCollection) do
        for _, event in ipairs(message.events) do
            if not TableContains(events, event) then
                numEvents = numEvents +  1
                events[numEvents] = event
            end
        end
    end
    return events
end

local MessageEvents = GetMessageEvents()

---@param frame MiniLootNSEventFrame
local function RegisterEvents(frame)
    for event, _ in pairs(EventHandlers) do
        pcall(frame.RegisterEvent, frame, event)
    end
end

---@param frame MiniLootNSEventFrame
local function UnregisterEvents(frame)
    for event, _ in pairs(EventHandlers) do
        pcall(frame.UnregisterEvent, frame, event)
    end
end

---@param onChatEvent MiniLootNSEventChatEventCallback
local function RegisterChatEvents(onChatEvent)
    local numEvents = #MessageEvents
    for i = numEvents, 1, -1 do
        local event = MessageEvents[i]
        local success = pcall(AddMessageEventFilter, event, onChatEvent)
        if not success then
            table.remove(MessageEvents, i)
        end
    end
end

---@param onChatEvent MiniLootNSEventChatEventCallback
local function UnregisterChatEvents(onChatEvent)
    local numEvents = #MessageEvents
    for i = numEvents, 1, -1 do
        local event = MessageEvents[i]
        local success = pcall(RemoveMessageEventFilter, event, onChatEvent)
        if not success then
            table.remove(MessageEvents, i)
        end
    end
end

---Registers the chat events directly on the frame. Used when a chat addon replaces the default chat frames and we can't rely on the message event filters.
---@param frame MiniLootNSEventFrame
local function RegisterFrameChatEvents(frame)
    for _, event in ipairs(MessageEvents) do
        pcall(frame.RegisterEvent, frame, event)
    end
end

---@param frame MiniLootNSEventFrame
local function UnregisterFrameChatEvents(frame)
    for _, event in ipairs(MessageEvents) do
        pcall(frame.UnregisterEvent, frame, event)
    end
end

---@param preview boolean
---@param event WowEvent
---@param ... any
---@return MiniLootMessageFormatSimpleParserResults?, MiniLootMessage?, boolean?
local function ResolveChatEvent(preview, event, ...)
    local text = ...
    local suppressRaw = suppressRawTransmogMessages > 0 and GetTime() <= suppressRawTransmogUntil
    if not preview and not suppressRaw then
        suppressRawTransmogMessages = 0
    end
    if event == "CHAT_MSG_LOOT" and suppressRaw and type(text) == "string" and IsSafeValue(text) and #text > 0 and #text <= 4 and not text:find("|", 1, true) then
        if not preview then
            suppressRawTransmogMessages = suppressRawTransmogMessages - 1
        end
        return nil, nil, true
    end

    local result, message = ProcessChatMessage(event, ...)
    if result then
        if not preview then
            ClearPendingSelfRoll(result, message)
        end
    else
        result, message = ProcessPendingSelfRoll(event, text, preview)
    end
    if not result or not message then
        return
    end
    local group = message.group
    if db.EnabledGroups[group] == false then
        return
    end
    if db.IgnoredGroups[group] or message.group == MiniLootMessageGroup.Ignore then
        return result, message, true
    end
    local isFiltered = EvaluateFilters(db.Filters, result, message)
    if isFiltered then
        return result, message, true
    end
    return result, message
end

function ProcessChatEvent(event, ...)
    return ResolveChatEvent(false, event, ...)
end

local function IsChatEventPreviewCacheable(event, text)
    -- A preview can depend on a pending roll or a short-lived raw suppression.
    return event ~= "CHAT_MSG_LOOT" or GetLootHistoryIDFromText(text) == nil
end

local function ShouldHideChatEvent(event, text)
    local result, _, hide = ResolveChatEvent(true, event, text)
    return hide or result ~= nil
end

local function SetSyntheticResultHandler(handler)
    syntheticResultHandler = handler
end

---@class MiniLootNSReporting
ns.Reporting = {
    EventHandlers = EventHandlers,
    MessageEvents = MessageEvents,
    RegisterEvents = RegisterEvents,
    UnregisterEvents = UnregisterEvents,
    RegisterChatEvents = RegisterChatEvents,
    UnregisterChatEvents = UnregisterChatEvents,
    RegisterFrameChatEvents = RegisterFrameChatEvents,
    UnregisterFrameChatEvents = UnregisterFrameChatEvents,
    ProcessChatEvent = ProcessChatEvent,
    IsChatEventPreviewCacheable = IsChatEventPreviewCacheable,
    ShouldHideChatEvent = ShouldHideChatEvent,
    EnsureLootRollHook = EnsureLootRollHook,
    SetSyntheticResultHandler = SetSyntheticResultHandler,
}
