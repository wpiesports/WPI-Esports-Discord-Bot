const { Client, Intents } = require('discord.js');
const dotenv = require('dotenv').config();
const Keyv = require('keyv');
const fs = require('fs');

const client = new Client({ intents: [Intents.FLAGS.GUILDS] });

client.once('ready', () => {
	console.log('Ready!');
});


client.login(process.env.DISCORD_TOKEN);