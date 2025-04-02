import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Grid, 
  Paper, 
  Box, 
  Card, 
  CardContent, 
  CardHeader,
  CircularProgress,
  Divider,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  Snackbar
} from '@mui/material';

const AISettings = () => {
  const [loading, setLoading] = useState(true);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });
  
  const [settings, setSettings] = useState({
    provider: 'openai',
    model: 'gpt-4',
    apiKey: '',
    useLocalAI: false,
    localAIEndpoint: 'http://localhost:11434',
    localAIModel: 'llama3',
    embeddingModel: 'text-embedding-3-small',
    maxTokens: 1000,
    temperature: 0.7
  });

  const handleChange = (event) => {
    const { name, value, checked } = event.target;
    setSettings({
      ...settings,
      [name]: name === 'useLocalAI' ? checked : value
    });
  };

  const handleSave = () => {
    // 실제 구현에서는 API 호출로 설정 저장
    console.log('Saving settings:', settings);
    
    setSnackbar({
      open: true,
      message: 'AI 설정이 저장되었습니다.',
      severity: 'success'
    });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({
      ...snackbar,
      open: false
    });
  };

  // 데이터 로딩 시뮬레이션
  useEffect(() => {
    // 실제 구현에서는 API 호출로 설정 로드
    setTimeout(() => {
      setLoading(false);
    }, 1000);
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" gutterBottom>
        AI 설정
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardHeader title="AI 서비스 설정" />
            <Divider />
            <CardContent>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth margin="normal">
                    <InputLabel>AI 제공자</InputLabel>
                    <Select
                      name="provider"
                      value={settings.provider}
                      onChange={handleChange}
                      label="AI 제공자"
                    >
                      <MenuItem value="openai">OpenAI</MenuItem>
                      <MenuItem value="mistral">Mistral AI</MenuItem>
                      <MenuItem value="gemini">Google Gemini</MenuItem>
                      <MenuItem value="local">로컬 AI</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth margin="normal">
                    <InputLabel>모델</InputLabel>
                    <Select
                      name="model"
                      value={settings.model}
                      onChange={handleChange}
                      label="모델"
                      disabled={settings.provider === 'local'}
                    >
                      {settings.provider === 'openai' && (
                        <>
                          <MenuItem value="gpt-4">GPT-4</MenuItem>
                          <MenuItem value="gpt-4-turbo">GPT-4 Turbo</MenuItem>
                          <MenuItem value="gpt-3.5-turbo">GPT-3.5 Turbo</MenuItem>
                        </>
                      )}
                      {settings.provider === 'mistral' && (
                        <>
                          <MenuItem value="mistral-large">Mistral Large</MenuItem>
                          <MenuItem value="mistral-medium">Mistral Medium</MenuItem>
                          <MenuItem value="mistral-small">Mistral Small</MenuItem>
                        </>
                      )}
                      {settings.provider === 'gemini' && (
                        <>
                          <MenuItem value="gemini-pro">Gemini Pro</MenuItem>
                          <MenuItem value="gemini-ultra">Gemini Ultra</MenuItem>
                        </>
                      )}
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="API 키"
                    name="apiKey"
                    value={settings.apiKey}
                    onChange={handleChange}
                    type="password"
                    margin="normal"
                    disabled={settings.provider === 'local'}
                    helperText={settings.provider === 'local' ? '로컬 AI 사용 시 API 키가 필요하지 않습니다.' : ''}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.useLocalAI}
                        onChange={handleChange}
                        name="useLocalAI"
                      />
                    }
                    label="로컬 AI 사용 (Ollama, LM Studio 등)"
                  />
                </Grid>
                
                {settings.useLocalAI && (
                  <>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="로컬 AI 엔드포인트"
                        name="localAIEndpoint"
                        value={settings.localAIEndpoint}
                        onChange={handleChange}
                        margin="normal"
                      />
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="로컬 AI 모델"
                        name="localAIModel"
                        value={settings.localAIModel}
                        onChange={handleChange}
                        margin="normal"
                        helperText="예: llama3, mistral, gemma 등"
                      />
                    </Grid>
                  </>
                )}
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12}>
          <Card>
            <CardHeader title="임베딩 설정" />
            <Divider />
            <CardContent>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth margin="normal">
                    <InputLabel>임베딩 모델</InputLabel>
                    <Select
                      name="embeddingModel"
                      value={settings.embeddingModel}
                      onChange={handleChange}
                      label="임베딩 모델"
                    >
                      <MenuItem value="text-embedding-3-small">OpenAI Text Embedding 3 Small</MenuItem>
                      <MenuItem value="text-embedding-3-large">OpenAI Text Embedding 3 Large</MenuItem>
                      <MenuItem value="local-embedding">로컬 임베딩 모델</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12}>
          <Card>
            <CardHeader title="생성 설정" />
            <Divider />
            <CardContent>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="최대 토큰 수"
                    name="maxTokens"
                    type="number"
                    value={settings.maxTokens}
                    onChange={handleChange}
                    margin="normal"
                    InputProps={{ inputProps: { min: 100, max: 4000 } }}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="온도 (Temperature)"
                    name="temperature"
                    type="number"
                    value={settings.temperature}
                    onChange={handleChange}
                    margin="normal"
                    InputProps={{ inputProps: { min: 0, max: 2, step: 0.1 } }}
                    helperText="0 (결정적) ~ 2 (창의적)"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
            <Button
              variant="contained"
              color="primary"
              onClick={handleSave}
              size="large"
            >
              설정 저장
            </Button>
          </Box>
        </Grid>
      </Grid>
      
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default AISettings;
