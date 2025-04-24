import { useState } from 'react'
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  VStack,
  Image,
  useToast
} from '@chakra-ui/react'
import axios from 'axios'

const TextToImage = () => {
  const [prompt, setPrompt] = useState('')
  const [negativePrompt, setNegativePrompt] = useState('')
  const [steps, setSteps] = useState(50)
  const [guidanceScale, setGuidanceScale] = useState(7.5)
  const [image, setImage] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const toast = useToast()

  const handleGenerate = async () => {
    try {
      setLoading(true)
      const response = await axios.post('/api/images/text-to-image', {
        prompt,
        negative_prompt: negativePrompt,
        num_inference_steps: steps,
        guidance_scale: guidanceScale
      })
      
      const imageData = response.data.image
      setImage(`data:image/png;base64,${imageData}`)
      
      toast({
        title: '生成成功',
        status: 'success',
        duration: 3000
      })
    } catch (error) {
      toast({
        title: '生成失败',
        description: error instanceof Error ? error.message : '未知错误',
        status: 'error',
        duration: 3000
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box>
      <VStack spacing={4} align="stretch">
        <FormControl>
          <FormLabel>提示词</FormLabel>
          <Input
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="输入提示词"
          />
        </FormControl>

        <FormControl>
          <FormLabel>反向提示词</FormLabel>
          <Input
            value={negativePrompt}
            onChange={(e) => setNegativePrompt(e.target.value)}
            placeholder="输入反向提示词"
          />
        </FormControl>

        <FormControl>
          <FormLabel>推理步数</FormLabel>
          <NumberInput
            value={steps}
            onChange={(_, value) => setSteps(value)}
            min={1}
            max={100}
          >
            <NumberInputField />
            <NumberInputStepper>
              <NumberIncrementStepper />
              <NumberDecrementStepper />
            </NumberInputStepper>
          </NumberInput>
        </FormControl>

        <FormControl>
          <FormLabel>引导系数</FormLabel>
          <NumberInput
            value={guidanceScale}
            onChange={(_, value) => setGuidanceScale(value)}
            min={1}
            max={20}
            step={0.1}
          >
            <NumberInputField />
            <NumberInputStepper>
              <NumberIncrementStepper />
              <NumberDecrementStepper />
            </NumberInputStepper>
          </NumberInput>
        </FormControl>

        <Button
          colorScheme="blue"
          onClick={handleGenerate}
          isLoading={loading}
          loadingText="生成中..."
        >
          生成图像
        </Button>

        {image && (
          <Box>
            <Image src={image} alt="生成的图像" />
          </Box>
        )}
      </VStack>
    </Box>
  )
}

export default TextToImage 