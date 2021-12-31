const { Client, Collection, Intents } = require('discord.js');
const dotenv = require('dotenv').config();
const Keyv = require('keyv');
const fs = require('fs');

// Database setup
const prefixes = new Keyv('redis://localhost:6379', { namespace: 'prefix' });
prefixes.on('error', err => console.error('Keyv connection error:', err));

// Client setup
const client = new Client({
	intents: [
		Intents.FLAGS.GUILDS,
		Intents.FLAGS.GUILD_MESSAGES,
		Intents.FLAGS.GUILD_MESSAGE_REACTIONS,
		Intents.FLAGS.DIRECT_MESSAGES,
		Intents.FLAGS.DIRECT_MESSAGE_REACTIONS
	],
	partials: ['CHANNEL']
});

// Event collection
const eventFiles = fs.readdirSync('./events').filter(file => file.endsWith('.js'));

// Command collection
client.commands = new Collection();
const commandFiles = fs.readdirSync('./commands').filter(file => file.endsWith('.js'));

for (const file of commandFiles) {
	const command = require(`./commands/${file}`);
	client.commands.set(command.type + command.data.name.toLowerCase(), command);

	if (command.data.aliases !== undefined) {
		for (const alias in command.data.aliases) {
			client.commands.set(command.type + alias.toLowerCase(), command);
		}
	}
}

// Slash command handler
client.on('interactionCreate', async interaction => {
	if (!interaction.isCommand()) return;

	const command = client.commands.get('slash' + interaction.commandName);

	if (!command) return;

	try {
		await command.execute(interaction);
	} catch (error) {
		console.error(error);
		await interaction.reply({ content: 'There was an error while executing this command!', ephemeral: true });
	}
});

// Prefix command handler
client.on('messageCreate', async message => {
	// Check for custom prefix
	let prefix = process.env.PREFIX
	if (message.guild !== null) {
		let prefix = await prefixes.get(message.guild.id)
		if (prefix === undefined) {
			prefix = process.env.PREFIX
		}
	}

	// Argument slicing + finding command
	const args = message.content.slice(prefix.length).split(/ +/);
	const commandName = args.shift().toLowerCase();
	if (!client.commands.has('prefix' + commandName)) return;
	const command = client.commands.get('prefix' + commandName);

	// Check for guild only
	if (command.data.guildOnly && message.channel.type !== 'GUILD_TEXT') {
		return message.reply('This command is guild only');
	}

	// Run the command
	command.execute(message, args);

});

// Event handler
for (const file of eventFiles) {
	const event = require(`./events/${file}`);
	if (event.once) {
		client.once(event.name, (...args) => event.execute(...args));
	} else {
		client.on(event.name, (...args) => event.execute(...args));
	}
}


client.login(process.env.DISCORD_TOKEN);