-- Usage:
--  default keybinding: n
--  add the following to your input.conf to change the default keybinding:
--  keyname script_binding highlight_sub-menu

local mp = require('mp')
local utils = require('mp.utils')
local sub = require('subtitle')

-- Config
-- Options can be changed here or in a separate config file.
-- Config path: ~/.config/mpv/script-opts/highlight_sub.conf
local config = {
    -- Change the following lines if the locations of executables differ from the defaults
    -- If set to empty, the path will be guessed.
    ffmpeg_path = "",
    ffsubsync_path = "",
    alass_path = "",

    -- Choose what tool to use. Allowed options: ffsubsync, alass, ask.
    -- If set to ask, the add-on will ask to choose the tool every time.
    audio_subsync_tool = "ask",
    altsub_subsync_tool = "ask",

    -- After retiming, tell mpv to forget the original subtitle track.
    unload_old_sub = true,
}

-- Snippet borrowed from stackoverflow to get the operating system
-- originally found at: https://stackoverflow.com/a/30960054
local os_name = (function()
    if os.getenv("HOME") == nil then
        return function()
            return "Windows"
        end
    else
        return function()
            return "*nix"
        end
    end
end)()

local os_temp = (function()
    if os_name() == "Windows" then
        return function()
            return os.getenv('TEMP')
        end
    else
        return function()
            return '/tmp/'
        end
    end
end)()

local function notify(message, level, duration)
    level = level or 'info'
    duration = duration or 1
    mp.msg[level](message)
    mp.osd_message(message, duration)
end

local function subprocess(args)
    return mp.command_native {
        name = "subprocess",
        playback_only = false,
        capture_stdout = true,
        args = args
    }
end

local function get_active_track(track_type)
    local track_list = mp.get_property_native('track-list')
    for num, track in ipairs(track_list) do
        if track.type == track_type and track.selected == true then
            return num, track
        end
    end
    return notify(string.format("Error: no track of type '%s' selected", track_type), "error", 3)
end

local function remove_extension(filename)
    return filename:gsub('%.%w+$', '')
end

local function get_extension(filename)
    return filename:match("^.+(%.%w+)$")
end

local function mkfp_c(sub_path)
    return table.concat { remove_extension(sub_path), '_c', get_extension(sub_path) }
end

local function extract_to_file(subtitle_track)
    local codec_ext_map = { subrip = "srt", ass = "ass" }
    local ext = codec_ext_map[subtitle_track['codec']]
    if ext == nil then
        return notify(string.format("Error: unsupported codec: %s", subtitle_track['codec']), "error", 3)
    end
    local temp_sub_fp = utils.join_path(os_temp(), 'highlight_sub_extracted.' .. ext)
    notify("Extracting internal subtitles...", nil, 3)
    local ret = subprocess {
        config.ffmpeg_path,
        "-hide_banner",
        "-nostdin",
        "-y",
        "-loglevel", "quiet",
        "-an",
        "-vn",
        "-i", mp.get_property("path"),
        "-map", "0:" .. (subtitle_track and subtitle_track['ff-index'] or 's'),
        "-f", ext,
        temp_sub_fp
    }
    if ret == nil or ret.status ~= 0 then
        return notify("Couldn't extract internal subtitle.\nMake sure the video has internal subtitles.", "error", 7)
    end
    return temp_sub_fp
end

local function highlight_subs()
    local _, track = get_active_track('sub')
    local file_path = track.external and track['external-filename'] or extract_to_file(track)
    local cwd = os.getenv("PWD")..'/'
    local codec_parser_map = { ass = sub.ASS, subrip = sub.SRT }
    local parser = codec_parser_map[track['codec']]
    local exe_command = "python ~/.config/mpv/scripts/Co-oringSubs/coloring_subs.py "..'"'..file_path..'"' 

    file_path = file_path:gsub('file://', '')

    notify("Coloring...", nil, 5)
    os.execute(exe_command)

    local s = parser:populate(mkfp_c(file_path))

    mp.commandv("sub_add", s.filename)
    s:save()
    notify("Complited")
end

mp.add_forced_key_binding("Alt+c", "highlight_subs", highlight_subs)
