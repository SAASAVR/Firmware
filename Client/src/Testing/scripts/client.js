//import { io } from "socket.io-client";
const io = require('socket.io-client')
var socket = io.connect('http://localhost:5000');

var output = function(event) {
    socket.emit('Slider value changed', {
        who: $(this).attr('id'),
        data: $(this).val()
    });
    return false;
}
