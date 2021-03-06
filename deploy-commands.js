const { REST } = require('@discordjs/rest');
const { Routes } = require('discord-api-types/v9');
const dotenv = require('dotenv').config();
const fs = require('fs');

const commands = [];
const globalCommands = [];

const rest = new REST({ version: '9' }).setToken(process.env.DISCORD_TOKEN);

const commandFiles = fs.readdirSync('./commands').filter(file => file.endsWith('.js'));

for (const file of commandFiles) {
    const command = require(`./commands/${file}`);
    if (command.type === 'slash') {
        if (command.global) {
            globalCommands.push(command.data.toJSON())
        }
        else {
            commands.push(command.data.toJSON());
        }
    }
}

rest.put(Routes.applicationGuildCommands(process.env.APPLICATION_ID, process.env.GUILD_ID), { body: commands })
    .then(() => console.log('Successfully registered guild application commands.'))
    .catch(console.error);

rest.put(Routes.applicationCommands(process.env.CLIENT_ID), { body: globalCommands})
    .then(() => console.log('Successfully registered application commands.'))
    .catch(console.error);