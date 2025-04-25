import asyncio
from pathlib import Path
from app.services.image_generator import ImageGenerator

async def main():
    # 创建图像生成器实例
    generator = ImageGenerator()
    
    # 生成图像
    prompt = """Central Theme
Theme: Epic fantasy battle scene with a young girl riding a majestic dragon.
Style: Dramatic and dynamic, with rich details and atmospheric lighting.
Scene Description:
Main Character: A brave young girl, around 10-12 years old, with flowing hair and determined expression, wearing fantasy armor.
Dragon: A magnificent dragon with iridescent scales, powerful wings, and fierce features. The dragon is in mid-flight, breathing fire.
Setting: An active volcano in the background, with lava flows and ash clouds creating an apocalyptic atmosphere.
Action: The girl and dragon are engaged in an epic battle against various mythical creatures.
Creatures: Multiple fantasy monsters including:
- Fire elementals emerging from lava
- Winged demons circling in the sky
- Rock golems emerging from the volcanic terrain
- Magma serpents coiling through the air
Lighting:
- Dramatic red-orange glow from the volcano and lava
- Flashes of dragon fire illuminating the scene
- Contrasting cool blue light from magical effects
Atmosphere:
- Dynamic composition with the dragon and girl as the focal point
- Epic scale showing the vastness of the battle
- Dramatic clouds of ash and smoke
- Magical energy effects and particle systems
Details:
- Intricate details on the dragon's scales and the girl's armor
- Expressive faces showing determination and courage
- Dynamic poses capturing the intensity of battle
- Rich environmental details in the volcanic landscape"""
    
    # 使用默认参数生成图像
    output_path = await generator.generate_image(prompt)
    print(f"图像已生成: {output_path}")
    
    # 使用自定义参数生成图像
    custom_output_path = Path("custom_output.png")
    output_path = await generator.generate_image_with_params(
        prompt=prompt,
        width=1024,
        height=1024,
        seed=123456,
        steps=30,
        output_path=custom_output_path
    )
    print(f"自定义参数图像已生成: {output_path}")

if __name__ == "__main__":
    asyncio.run(main()) 