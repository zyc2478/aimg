import { useState, useRef } from 'react'
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

const ImageToImage = () => {
  const [prompt, setPrompt] = useState('')
  const [strength, setStrength] = useState(0.75)
  const [inputImage, setInputImage] = useState<string | null>(null)
  const [outputImage, setOutputImage] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const toast = useToast()

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onloadend = () => {
        setInputImage(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleConvert = async () => {
    if (!inputImage) {
      toast({
        title: '请先上传图像',
        status: 'warning',
        duration: 3000
      })
      return
    }

    try {
      setLoading(true)
      
      // 将 base64 图像转换为文件
      const base64Data = inputImage.split(',')[1]
      const blob = await fetch(`data:image/png;base64,${base64Data}`).then(res => res.blob())
      const file = new File([blob], 'image.png', { type: 'image/png' })
      
      const formData = new FormData()
      formData.append('file', file)
      formData.append('prompt', prompt)
      formData.append('strength', strength.toString())
      
      const response = await axios.post('/api/images/image-to-image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      const imageData = response.data.image
      setOutputImage(`data:image/png;base64,${imageData}`)
      
      toast({
        title: '转换成功',
        status: 'success',
        duration: 3000
      })
    } catch (error) {
      toast({
        title: '转换失败',
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
          <FormLabel>上传图像</FormLabel>
          <Input
            type="file"
            accept="image/*"
            onChange={handleImageUpload}
            ref={fileInputRef}
          />
        </FormControl>

        {inputImage && (
          <Box>
            <Image src={inputImage} alt="输入图像" />
          </Box>
        )}

        <FormControl>
          <FormLabel>提示词</FormLabel>
          <Input
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="输入提示词"
          />
        </FormControl>

        <FormControl>
          <FormLabel>转换强度</FormLabel>
          <NumberInput
            value={strength}
            onChange={(_, value) => setStrength(value)}
            min={0}
            max={1}
            step={0.01}
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
          onClick={handleConvert}
          isLoading={loading}
          loadingText="转换中..."
        >
          转换图像
        </Button>

        {outputImage && (
          <Box>
            <Image src={outputImage} alt="转换后的图像" />
          </Box>
        )}
      </VStack>
    </Box>
  )
}

export default ImageToImage 