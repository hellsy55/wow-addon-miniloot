-- Offline behavior tests. Run from the repository root with Lua 5.1.
local ns = {}
local function loadModule(name)
    assert(loadfile(name .. ".lua"))("MiniLoot", ns)
end

format = string.format
LOOT, YOU, XP, HONOR = "Loot", "You", "XP", "Honor"
GOLD_AMOUNT, SILVER_AMOUNT, COPPER_AMOUNT = "%d Gold", "%d Silver", "%d Copper"
LARGE_NUMBER_SEPERATOR, DECIMAL_SEPERATOR = ",", "."
Settings = {}
WOW_PROJECT_ID, WOW_PROJECT_MAINLINE = 1, 1
Enum = { ItemQuality = { Common = 1, Rare = 3 }, ItemClass = { Gem = 3 } }
function table.wipe(values)
    for key in pairs(values) do values[key] = nil end
end
function CreateTextureMarkup() return "" end
function InCombatLockdown() return false end
function GetLocale() return "enUS" end
function GetBuildInfo() return "12.1.5", "99999", "", 120105 end
FormatLargeNumber = tostring

local time, timers = 0, {}
function GetTime() return time end
C_Timer = {}
function C_Timer.NewTimer(delay, callback)
    local timer = { at = time + delay, callback = callback }
    function timer:Cancel() self.cancelled = true end
    timers[#timers + 1] = timer
    return timer
end
C_Timer.After = C_Timer.NewTimer
local function advance(seconds)
    local untilTime = time + seconds
    while true do
        local nextIndex
        for index, timer in ipairs(timers) do
            if timer.at <= untilTime and (not nextIndex or timer.at < timers[nextIndex].at) then
                nextIndex = index
            end
        end
        if not nextIndex then break end
        local timer = table.remove(timers, nextIndex)
        time = timer.at
        if not timer.cancelled then timer.callback() end
    end
    time = untilTime
end

local item = "|Hitem:123|h[Test item]|h"
function GetLootRollItemLink() return item end
local hooks = {}
function hooksecurefunc(name, callback) hooks[name] = callback end
function RollOnLoot() end
function ConfirmLootRoll() end
function ChatFrame_AddMessageEventFilter() end
function ChatFrame_RemoveMessageEventFilter() end

LOOT_ROLL_NEED_SELF = "|HlootHistory:%d|h[Rolls]|h You selected Need for: %s"
LOOT_ROLL_YOU_WON_NO_SPAM_TRANSMOG = "|HlootHistory:%d|h[Rolls]|h Transmog (%d): %s"
COMBATLOG_XPGAIN_FIRSTPERSON_UNNAMED = "You gain %d experience."
COMBATLOG_XPGAIN_FIRSTPERSON = "%s dies, you gain %d experience."

loadModule("utils")
local remixSeason
ns.Utils.GetTimerunningSeasonID = function() return remixSeason end
ns.Utils.GetLootIcon = function(link) return link end
ns.Utils.IsQuestItem = function() return false end
loadModule("messages")
local groups = ns.Messages.MiniLootMessageGroup
loadModule("settings")
loadModule("filters")
loadModule("reporting")
loadModule("formatter")
loadModule("output")
local db = ns.Settings.db
db.Filters = {}

local function has(text, part)
    assert(text:find(part, 1, true), text .. " is missing " .. part)
end

local reporting = ns.Reporting
local process = reporting.ProcessChatEvent
local preview = reporting.ShouldHideChatEvent
local synthetic = {}
reporting.SetSyntheticResultHandler(function(result)
    synthetic[#synthetic + 1] = result
end)
reporting.EnsureLootRollHook()

hooks.RollOnLoot(1, 1)
local needText = format(LOOT_ROLL_NEED_SELF, 17, item)
assert(preview("CHAT_MSG_LOOT", needText))
local need = assert(process("CHAT_MSG_LOOT", needText))
assert(need.Type == "YouNeed" and need.LootHistory == 17 and need.Value == nil)
assert(not process("CHAT_MSG_LOOT", "|HlootHistory:17|h[Rolls]|h " .. item))

hooks.ConfirmLootRoll(2, 4)
local rawHistory = string.char(19)
assert(preview("CHAT_MSG_LOOT", rawHistory))
assert(not reporting.IsChatEventPreviewCacheable("CHAT_MSG_LOOT", rawHistory))
local transmog = assert(process("CHAT_MSG_LOOT", rawHistory))
assert(transmog.Type == "YouTransmog" and transmog.LootHistory == 19)
assert(not preview("CHAT_MSG_LOOT", rawHistory))
local winner, winnerMessage = process("CHAT_MSG_LOOT", format(LOOT_ROLL_YOU_WON_NO_SPAM_TRANSMOG, 20, 91, item))
assert(winner.Type == "YouTransmogResult" and winner.LootHistory == 20 and winner.ValueExtra == 91)
local formatted = ns.Formatter.Format(winnerMessage.group, { winner })
has(table.concat(formatted), "|HlootHistory:20|h")
has(table.concat(formatted), "Transmog (91)")
local ownRolls = ns.Formatter.Format(groups.LootRollYouDecide, {
    transmog, { Type = "YouTransmog", Link = item, LootHistory = 21 }, { Type = "YouTransmog", Link = item },
})
assert(#ownRolls == 3)
has(ownRolls[1], "|HlootHistory:19|h")
has(ownRolls[2], "|HlootHistory:21|h")
assert(not ownRolls[3]:find("|HlootHistory:", 1, true))

hooks.RollOnLoot(3, 4)
advance(0.1)
assert(#synthetic == 1 and synthetic[1].Type == "YouTransmog")
assert(preview("CHAT_MSG_LOOT", rawHistory))
assert(preview("CHAT_MSG_LOOT", rawHistory))
local result, _, suppress = process("CHAT_MSG_LOOT", rawHistory)
assert(not result and suppress)
assert(not preview("CHAT_MSG_LOOT", rawHistory))

local xpEvent = "CHAT_MSG_COMBAT_XP_GAIN"
local xpGroup = groups.Experience
local xpLines = {}
local xpOutput = ns.Output.CreateOutputHandler({ AddMessage = function(_, text) xpLines[#xpLines + 1] = text end })
local function outputExperience(result, message)
    assert(result.Type == "Experience" and result.Value == 120 and message.group == xpGroup)
    xpOutput:Add({ result = result, message = message })
end
reporting.SetSyntheticResultHandler(outputExperience)
local function turnIn(questID)
    reporting.EventHandlers.QUEST_TURNED_IN("QUEST_TURNED_IN", questID, 120, 0)
end
local function nativeExperience(text)
    local result, message, hide = process(xpEvent, text)
    assert(not hide)
    outputExperience(result, message)
    return result
end
local genericXP = format(COMBATLOG_XPGAIN_FIRSTPERSON_UNNAMED, 120)
local combatXP = format(COMBATLOG_XPGAIN_FIRSTPERSON, "Test creature", 120)

-- On an unverified build, a late native message and the fallback are both preserved.
db.DebounceGroups[xpGroup] = 0
turnIn(1)
assert(#xpLines == 1)
advance(5)
nativeExperience(genericXP)
assert(#xpLines == 2)

-- The reverse order gives the same result. Named combat XP is also preserved
-- even when its amount equals the quest reward and it arrives between turn-ins.
nativeExperience(genericXP)
turnIn(2)
assert(#xpLines == 4)
assert(nativeExperience(combatXP).Name == "Test creature")
assert(#xpLines == 5)

-- Equal rewards are individually handed to output and summed by the group timer.
db.DebounceGroups[xpGroup] = 1
turnIn(3)
turnIn(4)
assert(nativeExperience(combatXP).Name == "Test creature")
turnIn(5)
assert(#xpLines == 5)
advance(1)
assert(#xpLines == 6)
has(xpLines[6], "480")

db.Debounce = 2
db.DebounceGroups[groups.Experience] = 1
db.DebounceGroups[groups.LootRollYouDecide] = 0
local lines = {}
local output = ns.Output.CreateOutputHandler({ AddMessage = function(_, text) lines[#lines + 1] = text end })
output:Add({ message = { group = groups.Experience }, result = { Type = "Experience", Value = 7 } })
output:Add({ message = { group = groups.Honor }, result = { Type = "Honor", Value = 9 } })
output:Add({ message = { group = groups.LootRollYouDecide }, result = need })
assert(#lines == 1)
has(lines[1], "Need")
advance(1)
assert(#lines == 2)
has(lines[2], "7")
advance(1)
assert(#lines == 3)
has(lines[3], "9")

db.ChatFrame = "Chattynator:2:3"
db.Filters = { { group = groups.Loot, value = 4 } }
remixSeason = 1
db.ChatFrame = "Chattynator:1:2"
db.DebounceGroups[groups.Experience] = 5
assert(MiniLootRemixDB2.ChatFrame == "Chattynator:1:2")
assert(MiniLootDB2.ChatFrame == "Chattynator:2:3")
assert(MiniLootDB2.DebounceGroups[groups.Experience] == 1)
loadModule("settings")
assert(ns.Settings.db.DebounceGroups[groups.Experience] == 5)
remixSeason = nil
assert(ns.Settings.db.Filters[1].value == 4)
assert(ns.Settings.db.ChatFrame == "Chattynator:2:3")

local frame, filter, calls
function CreateFrame()
    frame = { RegisterEvent = function() end, UnregisterEvent = function() end, SetScript = function() end }
    return frame
end
ns.Utils.ChattynatorUtil = {
    IsLoaded = function() return true end,
    ResolveTarget = function() return 2, 3 end,
    AddFilter = function(_, handler) filter = handler end,
    RemoveFilter = function(_, handler) assert(handler == filter); filter = nil end,
    GetChattynatorHandler = function() end,
}
ns.Utils.GetChatFrames = function() return {} end
ns.UI = { SetupUI = function() end }
ns.Links = { Init = function() end }
ns.Tooltip = { EnableHyperlinks = function() end, DisableHyperlinks = function() end }
ns.Output.CreateOutputHandler = function() return { Add = function() end } end
calls = 0
reporting.ShouldHideChatEvent = function(event, text)
    calls = calls + 1
    return preview(event, text)
end
loadModule("init")
frame:OnEvent("ADDON_LOADED", "MiniLoot")
local xpData = { text = "You gain 17 experience.", typeInfo = { event = xpEvent } }
assert(filter(xpData) == false and filter(xpData) == false and calls == 1)
db.EnabledGroups[groups.Experience] = false
frame:OnSettingsChanged("EnabledGroups")
assert(filter(xpData) == true and filter(xpData) == true and calls == 2)
db.EnabledGroups[groups.Experience] = true

local rawData = { id = "roll-1", text = rawHistory, typeInfo = { event = "CHAT_MSG_LOOT" } }
assert(filter(rawData) == true)
hooks.RollOnLoot(4, 4)
assert(filter(rawData) == false and filter(rawData) == false)
frame:OnEvent("CHAT_MSG_LOOT", rawHistory)
assert(filter(rawData) == false)
assert(not preview("CHAT_MSG_LOOT", rawHistory))
advance(0)
assert(filter(rawData) == false)
assert(filter({ id = "roll-2", text = rawHistory, typeInfo = rawData.typeInfo }) == true)

print("Lua behavior tests passed (rolls, history, transmog, quest XP, chat filter, debounce, settings)")
