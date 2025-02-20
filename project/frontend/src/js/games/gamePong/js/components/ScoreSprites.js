import { GAME_SETTINGS } from '../config.js';

export function createScoreUI(scene, playerCount) {
	const { positions, colors, radius, textSize, textConfig } = GAME_SETTINGS.scoring.spriteConfig;
	const scoreSprites = [];
	for (let i = 0; i < playerCount; i++)
	{
		const position = positions[i];
		const color = colors[i];
		// create the circle background
		const circleGeometry = new THREE.CircleGeometry(radius, 30);
		const circleMaterial = new THREE.MeshBasicMaterial({
			color,
			transparent: true,
			opacity: textConfig.opacity,
		});
		const circle = new THREE.Mesh(circleGeometry, circleMaterial);
		circle.position.set(position.x, position.y, position.z - 0.1); // Slightly behind the text
		scene.add(circle);
		// create the text canvas
		const canvas = document.createElement('canvas');
		const context = canvas.getContext('2d');
		canvas.width = canvas.height = textConfig.canvasSize;
		// draw the text
		context.clearRect(0, 0, canvas.width, canvas.height); // Clear canvas
		context.fillStyle = textConfig.color; // Use text color from config
		context.font = textConfig.font; // Use font from config
		context.textAlign = 'center';
		context.textBaseline = 'middle';
		context.fillText('15', canvas.width / 2, canvas.height / 2); // Center text
		// create texture and sprite
		const texture = new THREE.CanvasTexture(canvas);
		texture.needsUpdate = true; // Mark the texture for update
		const spriteMaterial = new THREE.SpriteMaterial({ map: texture, transparent: true });
		const sprite = new THREE.Sprite(spriteMaterial);
		sprite.position.set(position.x, position.y, position.z);
		sprite.scale.set(radius * 1.8, radius * 1.8, 1); // Match circle size
		scene.add(sprite);
		// add both circle and sprite to the scoreSprites for later updates
		scoreSprites.push({ context, texture, sprite });
	}
	return scoreSprites;
}
/*
export function updateScoreText(context, score)
{
	const { font, color, canvasSize } = GAME_SETTINGS.scoring.spriteConfig.textConfig;
	context.clearRect(0, 0, canvasSize, canvasSize);
	context.fillStyle = color;
	context.font = font;
	context.textAlign = 'center';
	context.textBaseline = 'middle';
	// Draw the updated score
	context.fillText(score.toString(), canvasSize / 2, canvasSize / 2);
}
*/
export function updateScoreText(context, score)
{
    console.log(`🎯 Updating score text to: ${score}`);
    const { font, color, canvasSize } = GAME_SETTINGS.scoring.spriteConfig.textConfig;
    context.clearRect(0, 0, canvasSize, canvasSize);
    context.fillStyle = color;
    context.font = font;
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    // Draw the updated score
    context.fillText(score.toString(), canvasSize / 2, canvasSize / 2);
}