var system = require('system');
var args = system.args;

if (args.length === 1) {
    console.log('Try to pass some arguments when invoking this script!');
} else {
    args.forEach(function(arg, i) {
        if(arg.substring(0,4) == 'http') {
            console.log("Checking " + i + ": " + arg);
            var page = require('webpage').create();
            page.open(arg, function(status) {
                console.log("Status: " + status);
                if(status === "success") {
                    page.render('hellothere.png');
                    console.log('here');
                    phantom.exit();
                }
            });
        }
    });
}