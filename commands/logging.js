const { Permissions, WebhookClient} = require('discord.js');
const utilities = require('../utilities');
const Keyv = require('keyv');
const logging = new Keyv('redis://localhost:6379', { namespace: 'logging' });
logging.on('error', err => console.error('Keyv connection error:', err));


module.exports = {
    type: 'prefix',
    global: false,
    data: {
        name: 'logging',
        aliases: [],
        description: 'Top level command for logging',
        default_permission: Permissions.FLAGS.ADMINISTRATOR
    },
    async execute(message, args) {
        if (args.length === 0) {
            await subcommands.help.fn(message, args);
            return;
        }

        switch(args[0].toLowerCase()) {
            case 'help':
                await subcommands.help.fn(message);
                break;
            case 'set':
                await subcommands.set.fn(message, args);
                break;
            default:
                const prefix = await utilities.getPrefix(message.guild);
                await message.reply(`Did not recognize this command. Try \`${prefix}logging help\``)
        }
    },
};

// Subcommands
const subcommands = {
    help: {
        fn: async function(message, args) {
            const commandFields = []
            const prefix = await utilities.getPrefix(message.guild);
            for (const [key, value] of Object.entries(subcommands)) {
                commandFields.push({
                    name: `${prefix}${value.usage}`,
                    value: value.description,
                })
            }

            await message.reply({
                embeds: [{
                    color: 0x8899d4,
                    title: `Logging Commands`,
                    fields: commandFields,
                    footer: {
                        text: '<> = required, () = optional',
                    },
                    timestamp: new Date(),
                }]
            }).catch(console.error)
        },
        description: 'Gets command info',
        usage: `logging help (command)`
    },
    set: {
        fn: async function (message, args) {
            if (args.length < 2) {
                const prefix = await utilities.getPrefix(message.guild);
                await message.reply(`Not enough args. Try \`${prefix}logging set <channel>\``)
                return;
            }

            const channel = await utilities.getChannel(message, args[1])
            if (channel === null) {
                message.reply(`Could not find the channel \`${args[1]}\``);
                return
            }

            const webhookInfo = await logging.get(message.guild.id);
            if (channel.id === webhookInfo.channelId) {
                await message.reply("This channel is already being used for logging");
                return;
            }

            // Unregister old webhooks
            if (webhookInfo !== undefined) {
                const webhook = new WebhookClient({
                    id: webhookInfo.id,
                    token: webhookInfo.token
                });
                if (webhook !== undefined) {
                    await webhook.delete('Changing logging channel').catch();
                }
            }

            const webhook = await channel.createWebhook(
                'WPI Esports Logging',
                {
                    avatar: 'https://imgur.com/mRzpCB2',
                    reason: 'Adding a webhook for logging'
                })
                .then()
                .catch()
            if (webhook === undefined) {
                message.reply('Failed to create logging webhook. Do I have permissions?');
            }

            await logging.set(message.guild.id, {id: webhook.id, token: webhook.token, channelId: webhook.channelId})
            await message.reply(`Successfully set logging to ${channel}`)


        },
        description: 'Sets the logging channel to use',
        usage: `logging set <channel>`
    }
}




