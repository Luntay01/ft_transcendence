export async function loadGameSettings()
{
	try
	{
		const response = await fetch("/config/settings.json");
		if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
		
		const loadedSettings = await response.json();
		window.GAME_SETTINGS = loadedSettings;
		
		console.log("Game settings loaded:", window.GAME_SETTINGS);
	}
	catch (error)
	{
		console.log("Failed to load game settings:", error);
	}
}
