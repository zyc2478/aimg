import { useState } from 'react'
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  useToast
} from '@chakra-ui/react'
import axios from 'axios'

interface LoginProps {
  onLoginSuccess: () => void
}

const Login = ({ onLoginSuccess }: LoginProps) => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const toast = useToast()

  const handleLogin = async () => {
    try {
      setLoading(true)
      const response = await axios.post('/api/auth/token', {
        username,
        password
      })
      
      const { access_token } = response.data
      localStorage.setItem('token', access_token)
      
      toast({
        title: '登录成功',
        status: 'success',
        duration: 3000
      })
      
      onLoginSuccess()
    } catch (error) {
      toast({
        title: '登录失败',
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
          <FormLabel>用户名</FormLabel>
          <Input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="输入用户名"
          />
        </FormControl>

        <FormControl>
          <FormLabel>密码</FormLabel>
          <Input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="输入密码"
          />
        </FormControl>

        <Button
          colorScheme="blue"
          onClick={handleLogin}
          isLoading={loading}
          loadingText="登录中..."
        >
          登录
        </Button>
      </VStack>
    </Box>
  )
}

export default Login 