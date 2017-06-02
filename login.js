var confirmPermissions, debug, jqueryURI, page, system;

page = require('webpage').create();

system = require('system');

debug = true;

jqueryURI = "http://ajax.googleapis.com/ajax/libs/jquery/1.6.1/jquery.min.js";

if (debug) {
  page.onConsoleMessage = function(msg) {
    return console.log(msg);
  };
  page.onAlert = function(msg) {
    return console.log(msg);
  };
}

page.onUrlChanged = function(url) {
  var followUpURI;
  if (/settings\/account/.test(url)) {
    console.log("logged in " + system.args[1]);
    followUpURI = system.args[3];
    return setTimeout(function() {
      return confirmPermissions(followUpURI);
    }, 1);
  }
};

page.open("https://accounts.google.com/ServiceLogin", function(status) {
  if (status === "success") {
    page.includeJs(jqueryURI, function() {
      return page.evaluate(function(username, password) {
        $("input").each(function() {
          return console.log("input", $(this).attr("type"), this.id, this.name, $(this).val());
        });
        $("input[type=email]").val(username);
        $("input[type=password]").val(password);
        return $("input[type=submit]").click();
      }, system.args[1], system.args[2]);
    });
    return setTimeout(function() {
      page.render("timeout.png");
      console.log("TIMEOUT! See timeout.png.");
      return phantom.exit(1);
    }, 15000);
  } else {
    console.log("... fail! Check the $PWD?!");
    return phantom.exit(1);
  }
});

confirmPermissions = function(uri) {
  var confirmPage;
  console.log("navigating to: " + uri);
  confirmPage = require('webpage').create();
  confirmPage.onConsoleMessage = function(msg) {
    return console.log(msg);
  };
  confirmPage.onAlert = function(msg) {
    return console.log(msg);
  };
  confirmPage.onUrlChanged = function(url) {
    return console.log("*NEW* confirm url " + url);
  };
  return confirmPage.open(uri, function(status) {
    var pos;
    console.log(status);
    if (status !== "success") {
      console.log("page failed to load, see fail.png");
      confirmPage.render("fail.png");
      phantom.exit(1);
    }
    pos = null;
    confirmPage.includeJs(jqueryURI, function() {
      return pos = confirmPage.evaluate(function() {
        var button, height, left, ref, ref1, top, width;
        $("button").each(function() {
          return console.log("button", $(this).attr("type"), this.id, this.name, $(this).val());
        });
        button = $('#submit_approve_access').first();
        ref = button.offset(), left = ref.left, top = ref.top;
        ref1 = [button.width(), button.height()], width = ref1[0], height = ref1[1];
        return {
          x: Math.round(left + width / 2),
          y: Math.round(top + height / 2)
        };
      });
    });
    return setTimeout(function() {
      console.log("approving by clicking at", pos.x, pos.y);
      return confirmPage.sendEvent('click', pos.x, pos.y);
    }, 2000);
  });
};
RunLink