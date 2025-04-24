import { Box, Container, Heading, Tabs, TabList, TabPanels, Tab, TabPanel } from '@chakra-ui/react'
import TextToImage from './components/TextToImage'
import ImageToImage from './components/ImageToImage'

function App() {
  return (
    <Container maxW="container.xl" py={8}>
      <Heading as="h1" size="xl" mb={8} textAlign="center">
        AI 图像生成
      </Heading>
      
      <Tabs isFitted variant="enclosed">
        <TabList mb="1em">
          <Tab>文本生成图像</Tab>
          <Tab>图像转换</Tab>
        </TabList>
        
        <TabPanels>
          <TabPanel>
            <TextToImage />
          </TabPanel>
          <TabPanel>
            <ImageToImage />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Container>
  )
}

export default App 