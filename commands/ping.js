const { SlashCommandBuilder } = require('@discordjs/builders');

module.exports = {
    type: 'slash',
    global: true,
    data: new SlashCommandBuilder()
        .setName('ping')
        .setDescription('Gives the bots response time'),
    async execute(interaction) {
        await interaction.reply({
            content: `Message: ${interaction.createdTimestamp - Date.now()}ms\nAPI: ${Math.round(interaction.client.ws.ping)}ms`,
            ephemeral: true
        });
    },
};