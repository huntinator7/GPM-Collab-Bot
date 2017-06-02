const Discord = require('discord.js');
const bot = new Discord.Client();

bot.login('MzA2NDgzMzM0MzYyNTYyNTYw.DBIJEQ.A7jRc5ODaLNxqM1RUVUA3JwhkRY');

bot.on('message', (message) => {

    if(message.content.startsWith('$see ')) {
        //message.reply(message.content.substring(5) + ' ' + accessWebpage(message.content.substring(4)));
        message.reply("Success.");
        accessWebpage(message.content.substring(5));
    }

});

function accessWebpage(site) {
    const spawn = require('child_process').spawn;
    console.log(site);
    const proc = spawn('phantomjs', ['hello.js', '--ssl-protocol=any', site]);

    proc.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
    });

    proc.stderr.on('data', (data) => {
        console.log(`stderr: ${data}`);
    });

    proc.on('close', (code) => {
        console.log(`child process exited with code ${code}`);
    });
}