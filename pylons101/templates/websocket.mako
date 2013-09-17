<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
</head>
<p id="log" style="width: 100%; background-color: #aaaaaa; font-size: 2em;">content goes in here</p>
<body>
<script src="http://code.jquery.com/jquery-1.8.2.min.js"></script>
<button id="open" style='width: 400px; height:  200px;'>OPEN</button>
<button id="close" style='width: 400px; height:  200px;'>CLOSE</button>
<script>
    function log(txt) {
        $("p#log").html('<div>' + txt + '</div>');
    }
    $(document).ready(function(){
        $(document).on('click', '#open', function () {
            $("p#log").html('');
            var ws = new WebSocket("ws://" + document.domain + ":5000/ws");
            ws.onmessage = function (msg) { log(msg.data); };
            ws.onclose = function () {  };
            window.onbeforeunload = function() {
                ws.close()
            };
            window.ws = ws;
            log('opened');
        });
        $(document).on('click', '#close', function() {
            window.ws.close();
            log('closed ' + window.ws);
        });
    });
</script>
</body>
</html>