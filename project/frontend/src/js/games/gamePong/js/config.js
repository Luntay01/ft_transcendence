/*
export const DEBUG = false;

export const GAME_SETTINGS = {
	ballPhysics: {
		initialVelocity: { x: 1.5, y: 0, z: 1.2 },
		bounds: { minX: -15, maxX: 15, minZ: -15, maxZ: 15 },//  TODO: increase values when done with testing
		scale: 0.9,
		maxSpeed: 20,
		rotationMultiplier: 1.0,
	},
	playerConfig: {
		positions: {
			bottom: { x: 0, y: 0, z: 10, rotationY: 0, movementDirection: 'horizontal' },
			top: { x: 0, y: 0, z: -10, rotationY: Math.PI, movementDirection: 'horizontal' },
			left: { x: -10, y: 0, z: 0, rotationY: -Math.PI / 2, movementDirection: 'vertical' },
			right: { x: 10, y: 0, z: 0, rotationY: Math.PI / 2, movementDirection: 'vertical' },
		},
		playerColors: ['#2A1A14', '#1E1E1E', '#10224E', '#1A0D20'],
		bounds: {
			bottom: { minX: -7, maxX: 7, minZ: 8, maxZ: 12 },
			top: { minX: -7, maxX: 7, minZ: -12, maxZ: -8 },
			left: { minX: -12, maxX: -8, minZ: -7, maxZ: 7 },
			right: { minX: 8, maxX: 12, minZ: -7, maxZ: 7 },
		},
		speedMultiplier: 1.0,
	},
	collision: {
		ballRadius: 0.2,
		flowerPotRadius: 1.2,
		gardenBedRadius: 2.1,
		reboundFactor: 1.1, // bounce intensity
		dampingFactor: 1.01, // velocity multiplier for flower pots
		minimumSpeed: 1.0,  // minimum velocity for the ball
	},
	scoring: {
		startingScore: 15,
		spriteConfig: {
			radius: 40,
			textSize: 100,
			textConfig: {
				font: 'bold 100px Arial',
				color: 'black', 
				canvasSize: 256, 
				opacity: 0.8,
			},
			positions: [
				{ x: -500, y: 450, z: 2 },
				{ x: -200, y: 450, z: 2 },
				{ x: 200, y: 450, z: 2 },
				{ x: 500, y: 450, z: 2 }
			],
			colors: ['#C8643A', '#A0A0A0', '#5B92D8', '#6A206E'], // player-specific colors
		},
	},
	grass: {
		rows: 80,
		columns: 80,
		randomPositionOffset: 0.15,
		randomTiltX: 0.2,
		randomTiltY: Math.PI * 2,
		randomTiltZ: 0.2,
		defaultScale: 0.9,
		color: 0x009000,
		reactionRadius: 1.0,
	},
	lighting: {
		directionalLight: {
			color: 0xffffff,
			intensity: 5,
			position: { x: 10, y: 10, z: 10 },
		},
		ambientLight: {
			color: 0xffffff,
			intensity: 0.5,
		},
		backgroundColor: 0x009900,
	},
	animations: {
		tiltSpeed: 1.0,
		returnSpeed: 1.5,
	},
	modelPaths: {
		flowerPot: '/js/games/gamePong/assets/models/flower_pot.glb',
		gardenBed: '/js/games/gamePong/assets/models/garden_bed.glb',
		grassBlade: '/js/games/gamePong/assets/models/grass_blade.glb',
		fertilizerBall: '/js/games/gamePong/assets/models/fertilizer_ball.glb',
	},
	sounds: {
		collision: '/js/games/gamePong/assets/collision.mp3',//doens exist
		goal: '/js/games/gamePong/assets/goal.mp3',//doens exist
	},
	cameraStates: {
		bottom: { position: { x: 0, y: 11, z: 17 }, lookAt: { x: 0, y: -2, z: 0 } },
		top: { position: { x: 0, y: 11, z: -17 }, lookAt: { x: 0, y: -2, z: 0 } },
		left: { position: { x: -17, y: 11, z: 0 }, lookAt: { x: 0, y: -2, z: 0 } },
		right: { position: { x: 17, y: 11, z: 0 }, lookAt: { x: 0, y: -2, z: 0 } },
		spectator: { position: { x: 0, y: 30, z: 0 }, lookAt: { x: 0, y: 0, z: 0 } },
	},
};

export default { DEBUG, GAME_SETTINGS };
*/

//variable now stored in /config/settings.json

export const DEBUG = false;

export const GAME_SETTINGS = {
	ballPhysics: {
		initialVelocity: null,
		bounds: null,
		scale: null,
		maxSpeed: null,
		minBallSpeed: null,
		rotationMultiplier: null,
		maxBalls: null,
	},
	playerConfig: {
		positions: {
			bottom: null,
			top: null,
			left: null,
			right: null,
		},
		playerColors: null,
		bounds: {
			bottom: null,
			top: null,
			left: null,
			right: null,
		},
		speedMultiplier: null,
	},
	collision: {
		ballRadius: null,
		flowerPotRadius: null,
		gardenBedRadius: null,
		reboundFactor: null,
		dampingFactor: null,
		minimumSpeed: null,
		ejectForce: null,
	},
	scoring: {
		startingScore: null,
		goalZones: {
			bottom: { minX: null, maxX: null, minZ: null, maxZ: null, playerId: null },
			top: { minX: null, maxX: null, minZ: null, maxZ: null, playerId: null },
			left: { minX: null, maxX: null, minZ: null, maxZ: null, playerId: null },
			right: { minX: null, maxX: null, minZ: null, maxZ: null, playerId: null }
		},
		spriteConfig: {
			radius: null,
			textSize: null,
			textConfig: {
				font: null,
				color: null,
				canvasSize: null,
				opacity: null,
			},
			positions: [
				{ x: null, y: null, z: null },
				{ x: null, y: null, z: null },
				{ x: null, y: null, z: null },
				{ x: null, y: null, z: null }
			],
			colors: null,
		},
	},
	grass: {
		rows: null,
		columns: null,
		randomPositionOffset: null,
		randomTiltX: null,
		randomTiltY: null,
		randomTiltZ: null,
		defaultScale: null,
		color: null,
		reactionRadius: null,
	},
	gardenBeds: {
		positions: [
			{ x: null, y: null, z: null }, 
			{ x: null, y: null, z: null }, 
			{ x: null, y: null, z: null }, 
			{ x: null, y: null, z: null }
		],
		radius: 2.1
	},
	lighting: {
		directionalLight: {
			color: null,
			intensity: null,
			position: { x: null, y: null, z: null },
		},
		ambientLight: {
			color: null,
			intensity: null,
		},
		backgroundColor: null,
	},
	animations: {
		tiltSpeed: null,
		returnSpeed: null,
	},
	modelPaths: {
		flowerPot: null,
		gardenBed: null,
		grassBlade: null,
		fertilizerBall: null,
	},
	sounds: {
		collision: null,
		goal: null,
	},
	cameraStates: {
		bottom: { position: { x: null, y: null, z: null }, lookAt: { x: null, y: null, z: null } },
		top: { position: { x: null, y: null, z: null }, lookAt: { x: null, y: null, z: null } },
		left: { position: { x: null, y: null, z: null }, lookAt: { x: null, y: null, z: null } },
		right: { position: { x: null, y: null, z: null }, lookAt: { x: null, y: null, z: null } },
		spectator: { position: { x: null, y: null, z: null }, lookAt: { x: null, y: null, z: null } },
	},
};

function mergeSettings(target, source)
{
	for (const key in source)
	{
		if (Array.isArray(source[key]))
			target[key] = [...source[key]];
		else if (typeof source[key] === 'object' && source[key] !== null)
		{
			if (!target[key]) target[key] = {};
				mergeSettings(target[key], source[key]);
		}
		else
			target[key] = source[key];
	}
}

export async function loadGameSettings()
{
	try
	{
		const response = await fetch("/config/settings.json");
		if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
		const loadedSettings = await response.json();
		mergeSettings(GAME_SETTINGS, loadedSettings);
		console.log("Loaded and merged game settings:", GAME_SETTINGS);
	}
	catch (error)
	{
		console.error("Failed to load game settings:", error);
	}
}

await loadGameSettings();
export default { DEBUG, GAME_SETTINGS };


