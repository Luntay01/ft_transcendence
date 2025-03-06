/*
 Converts an http/https url to a ws/wss url
*/
export function getWebsocketURI(s) {
    var l = window.location;
    return ((l.protocol === "https:") ? "wss://" : "ws://") + l.host + s;
}
