-- Lua script to add timestamp if not present
function add_timestamp(tag, timestamp, record)
    if record["timestamp"] == nil and record["@timestamp"] == nil then
        record["@timestamp"] = os.date("!%Y-%m-%dT%H:%M:%S.000Z")
    end
    return 1, timestamp, record
end
