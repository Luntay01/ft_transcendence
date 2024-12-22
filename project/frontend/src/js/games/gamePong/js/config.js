export const DEBUG = true;

export const GAME_SETTINGS = {
	ballPhysics: {
		initialVelocity: { x: 1.5, y: 0, z: 1.2 },
		bounds: { minX: -2, maxX: 2, minZ: -20, maxZ: 20 },//  TODO: increase values when done with testing
		scale: 0.9,
		maxSpeed: 20,
	},
	playerConfig: {
		positions: {
			bottom: { x: 0, y: 0, z: 10, rotationY: 0, movementDirection: 'horizontal' },
			top: { x: 0, y: 0, z: -10, rotationY: Math.PI, movementDirection: 'horizontal' },
			left: { x: -10, y: 0, z: 0, rotationY: -Math.PI / 2, movementDirection: 'vertical' },
			right: { x: 10, y: 0, z: 0, rotationY: Math.PI / 2, movementDirection: 'vertical' },
		},
		bounds: {
			bottom: { minX: -7, maxX: 7, minZ: 8, maxZ: 12 },
			top: { minX: -7, maxX: 7, minZ: -12, maxZ: -8 },
			left: { minX: -12, maxX: -8, minZ: -7, maxZ: 7 },
			right: { minX: 8, maxX: 12, minZ: -7, maxZ: 7 },
		},
		speedMultiplier: 1.0,
	},
	collision: {
		ballRadius: 0.5,
		flowerPotRadius: 1.0,
		gardenBedRadius: 2.0,
		reboundFactor: 1.1, // bounce intensity
	},
	scoring: {
		scoreToWin: 15,
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
		bottom: { position: { x: 0, y: 9, z: 16 }, lookAt: { x: 0, y: -4, z: 0 } },
		top: { position: { x: 0, y: 9, z: -16 }, lookAt: { x: 0, y: -4, z: 0 } },
		left: { position: { x: -16, y: 9, z: 0 }, lookAt: { x: 0, y: -4, z: 0 } },
		right: { position: { x: 16, y: 9, z: 0 }, lookAt: { x: 0, y: -4, z: 0 } },
	},
};

export default { DEBUG, GAME_SETTINGS };