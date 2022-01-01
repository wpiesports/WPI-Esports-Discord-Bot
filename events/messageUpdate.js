const { WebhookClient } = require('discord.js');
const Keyv = require('keyv');
const logging = new Keyv('redis://localhost:6379', { namespace: 'logging' });
logging.on('error', err => console.error('Keyv connection error:', err));

module.exports = {
    name: 'messageUpdate',
    async execute(oldMessage, newMessage) {
        // Check if message is from bot
        if (newMessage.author.bot) return;

        // Check if logging is enabled
        const webhook_info = await logging.get(newMessage.guild.id);
        if (webhook_info === undefined) { return; }

        // Load webhook
        const webhook = new WebhookClient({
            id: webhook_info.id,
            token: webhook_info.token
        });
        if (webhook === undefined) { return; }

        let embedList = [];

        // Check for a content update
        if (oldMessage.content !== newMessage.content) {
            // Check length of the content (embed description max character length 4096)
            const description = `**Before:** ${oldMessage.content}\n**+After:** ${newMessage.content}\n[Go To](${newMessage.url})`;

            if (description.length > 4096) {
                embedList.push({
                    color: 0x8899d4,
                    title: `Message edited in #${newMessage.channel.name} (1/2)`,
                    author: {
                        name: `${newMessage.author.username}#${newMessage.author.discriminator}`,
                        icon_url: `${newMessage.author.avatarURL(dynamic=true)}`,
                    },
                    description: `**Before:** ${oldMessage.content}\n[Go To](${newMessage.url})`,
                    timestamp: new Date(),
                    footer: {
                        text: `​        User ID: ${newMessage.author.id}\n​ Channel ID: ${newMessage.channel.id}\nMessage ID: ${newMessage.id}`,
                    }
                });
                embedList.push({
                    color: 0x8899d4,
                    title: `Message edited in #${oldMessage.channel.name} (2/2)`,
                    author: {
                        name: `${newMessage.author.username}#${newMessage.author.discriminator}`,
                        icon_url: `${newMessage.author.avatarURL(dynamic=true)}`,
                    },
                    description: `**+After:** ${newMessage.content}\n[Go To](${message.url})`,
                    timestamp: new Date(),
                    footer: {
                        text: `​        User ID: ${newMessage.author.id}\n​ Channel ID: ${newMessage.channel.id}\nMessage ID: ${newMessage.id}`,
                    }
                });
            }
            else {
                embedList.push({
                    color: 0x8899d4,
                    title: `Message edited in #${oldMessage.channel.name}`,
                    author: {
                        name: `${newMessage.author.username}#${newMessage.author.discriminator}`,
                        icon_url: `${newMessage.author.avatarURL(dynamic=true)}`,
                    },
                    description: description,
                    timestamp: new Date(),
                    footer: {
                        text: `​        User ID: ${newMessage.author.id}\n​ Channel ID: ${newMessage.channel.id}\nMessage ID: ${newMessage.id}`,
                    }
                });
            }

        }

        // Check for message pin / unpin
        if (oldMessage.pinned !== newMessage.pinned) {
            if (newMessage.pinned) {
                embedList.push({
                    color: 0x43b581,
                    title: `Message pinned in #${oldMessage.channel.name}`,
                    User: {
                        name: `${newMessage.author.username}#${newMessage.author.discriminator}`,
                        icon_url: `${newMessage.author.avatarURL(dynamic=true)}`,
                    },
                    description: `${newMessage.content}\n[Go To](${newMessage.url})`,
                    timestamp: new Date(),
                    footer: {
                        text: `​        User ID: ${newMessage.author.id}\n​ Channel ID: ${newMessage.channel.id}\nMessage ID: ${newMessage.id}`,
                    }
                });
            }
            else {
                embedList.push({
                    color: 0xbe4041,
                    title: `Message unpinned in #${oldMessage.channel.name}`,
                    User: {
                        name: `${newMessage.author.username}#${newMessage.author.discriminator}`,
                        icon_url: `${newMessage.author.avatarURL(dynamic=true)}`,
                    },
                    description: `${newMessage.content}\n[Go To](${newMessage.url})`,
                    timestamp: new Date(),
                    footer: {
                        text: `​        User ID: ${newMessage.author.id}\n​ Channel ID: ${newMessage.channel.id}\nMessage ID: ${newMessage.id}`,
                    }
                });
            }
        }

        // Check for attachment removal
        if (oldMessage.attachments.size != newMessage.attachments.size) {
            let attachmentFields = []

            for (const attachment of oldMessage.attachments.difference(newMessage.attachments)) {
                attachmentFields.push({
                    name: attachment[1].name,
                    value: `Type: ${attachment[1].contentType}\nSpoiler: ${attachment[1].spoiler}\nURL: ${attachment[1].proxyURL}`,
                    inline: false
                })
            }
            embedList.push({
                color: 0xbe4041,
                title: `Attachment(s) removed in #${newMessage.channel.name}`,
                User: {
                    name: `${newMessage.author.username}#${newMessage.author.discriminator}`,
                    icon_url: `${newMessage.author.avatarURL(dynamic=true)}`,
                },
                description: `[Go To] (${newMessage.url})`,
                fields: attachmentFields,
                timestamp: new Date(),
                footer: {
                    text: `​        User ID: ${newMessage.author.id}\n​ Channel ID: ${newMessage.channel.id}\nMessage ID: ${newMessage.id}`,
                }
            })
        }

        // Send embeds
        if (embedList.length > 0) {
            await webhook.send({
                embeds: embedList
            })
        }
    }
}