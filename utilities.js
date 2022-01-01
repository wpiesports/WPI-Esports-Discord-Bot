const dotenv = require('dotenv').config();
const Keyv = require('keyv');
const prefixes = new Keyv('redis://localhost:6379', { namespace: 'prefix' });
prefixes.on('error', err => console.error('Keyv connection error:', err));

module.exports = {
    getPrefix: async function(guild) {
        let prefix = process.env.PREFIX
        if (guild !== null) {
            let prefix = await prefixes.get(guild.id)
            if (prefix === undefined) {
                return process.env.PREFIX
            }
            return prefix
        }
    },
    getChannel: async function(message, channelInfo) {
        let channel;

        // Mention check
        if (/^<#\d{18}>/.test(channelInfo)) {
            channel = await message.guild.channels.fetch(channelInfo.replace(/\D/g,''))
                .then()
                .catch();
            if (channel !== undefined) {
                return channel;
            }

        }

        // ID check
        if (/^\d{18}/.test(channelInfo)) {
            channel = await message.guild.channels.fetch(channelInfo)
                .then()
                .catch();
            if (channel !== undefined) {
                return channel;
            }
        }

        // Name check
        channel = await message.client.channels.cache.find(channel => channel.name === channelInfo);
        if (channel !== undefined) {
            return channel;
        }

        return null;
    }
}

