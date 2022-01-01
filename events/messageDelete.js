const { WebhookClient } = require('discord.js');
const Keyv = require('keyv');
const logging = new Keyv('redis://localhost:6379', { namespace: 'logging' });
logging.on('error', err => console.error('Keyv connection error:', err));

module.exports = {
    name: 'messageDelete',
    async execute(message) {
        // Check if a message is from bot
        if (message.author.bot) return;

        // Check if logging is enabled
        const webhook_info = await logging.get(message.guild.id);
        if (webhook_info === undefined) { return; }

        // Load webhook
        const webhook = new WebhookClient({
            id: webhook_info.id,
            token: webhook_info.token
        });
        if (webhook === undefined) { return; }

        // Main embed
        const embed = {
            color: 0xbe4041,
            title: `Message deleted in #${message.channel.name}`,
            author: {
                name: `${message.author.username}#${message.author.discriminator}`,
                icon_url: `${message.author.avatarURL()}`,
            },
            description: message.content,
            fields: [],
            timestamp: new Date(),
            footer: {
                text: `​        User ID: ${message.author.id}\n​ Channel ID: ${message.channel.id}\nMessage ID: ${message.id}`,
            }
        }

        // Attachment fields
        if (message.attachments.size > 0) {
            for (const attachment of message.attachments) {
                embed.fields.push({
                    name: `Attachment ${attachment[1].name}`,
                    value: `Type: ${attachment[1].contentType}\nSpoiler: ${attachment[1].spoiler}\n${attachment[1].proxyURL}`,
                    inline: false
                });
            }
        }

        // Activities
        if (message.activity != null) {
            embed.fields.push({
                name: 'Activity',
                value: `${message.activity.partyId.slice(0, message.activity.partyId.indexOf(':'))}`,
                inline: false
            });
        }

        // Send
        await webhook.send({
            embeds: [embed]
        }).catch(console.error);
    }
};