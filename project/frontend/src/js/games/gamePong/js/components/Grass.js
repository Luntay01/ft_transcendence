
class Grass
{
	constructor(bladeModel, rows, columns) {
		this.rows = rows;
		this.columns = columns;
	
		// Extract geometry from the child of the loaded model
		const child = bladeModel.children[0]; // Assuming the first child contains the geometry
		if (child && child.geometry)
		{
			this.geometry = child.geometry.clone(); // Clone geometry
			this.geometry.rotateX(Math.PI / 2); // Rotate upright
			this.material = new THREE.MeshBasicMaterial({
				color: 0x009000, // Green color
				side: THREE.DoubleSide, // Render both sides of the plane
			});
		}
	
		this.instanceMesh = null; // InstancedMesh for performance
	}

	createGrassField()
	{
		if (!this.geometry || !this.material)
		{
			console.error('Grass geometry or material is missing.');
			return null;
		}
		this.instanceMesh = new THREE.InstancedMesh(
			this.geometry,
			this.material,
			this.rows * this.columns
		);
		const dummy = new THREE.Object3D();
		let index = 0;
		for (let i = 0; i < this.rows; i++) {
			for (let j = 0; j < this.columns; j++)
			{
				dummy.position.set(
					(i - this.rows / 2) * 0.25 + Math.random() * 0.15,
					0,
					(j - this.columns / 2) * 0.25 + Math.random() * 0.15
				);
				dummy.rotation.set(
					(Math.random() - 0.5) * 0.2, // Small tilt on the X-axis
					Math.random() * Math.PI * 2, // Random rotation around the Y-axis
					(Math.random() - 0.5) * 0.2  // Small tilt on the Z-axis
				);
				const scale = 0.9;// + Math.random() * 0.6;
				dummy.scale.set(scale, scale, scale);
				dummy.updateMatrix();
				this.instanceMesh.setMatrixAt(index++, dummy.matrix);
			}
		}
		this.instanceMesh.instanceMatrix.needsUpdate = true;
		return this.instanceMesh;
	}

	respondToBall(ballPositions)
	{
		const dummy = new THREE.Object3D();
		ballPositions.forEach((ballPos) => {
			for (let i = 0; i < this.instanceMesh.count; i++)
			{
				this.instanceMesh.getMatrixAt(i, dummy.matrix);
				const bladePos = new THREE.Vector3().setFromMatrixPosition(dummy.matrix);
				const distance = bladePos.distanceTo(ballPos);
				if (distance < 1)
				{
					dummy.rotation.x = -0.3 * (1 - distance); // Tilt more for closer distances
					dummy.updateMatrix();
					this.instanceMesh.setMatrixAt(i, dummy.matrix);
				}
			}
		});
		this.instanceMesh.instanceMatrix.needsUpdate = true;
	}
}

export default Grass;