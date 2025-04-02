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
  Snackbar,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle
} from '@mui/material';
import TelegramIcon from '@mui/icons-material/Telegram';
import NotificationsIcon from '@mui/icons-material/Notifications';
import StorageIcon from '@mui/icons-material/Storage';
import BackupIcon from '@mui/icons-material/Backup';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import AddIcon from '@mui/icons-material/Add';
import SaveIcon from '@mui/icons-material/Save';

const Settings = () => {
  const [loading, setLoading] = useState(true);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogType, setDialogType] = useState('');
  const [dialogData, setDialogData] = useState({});
  
  const [settings, setSettings] = useState({
    telegram: {
      enabled: true,
      botToken: '1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ',
      chatId: '123456789',
      notifyOnMarketOpen: true,
      notifyOnMarketClose: true,
      notifyOnSignificantChange: true,
      significantChangeThreshold: 5,
      dailyReportTime: '18:00',
      weeklyReportDay: 'friday',
      weeklyReportTime: '18:00',
      monthlyReportDay: 1,
      monthlyReportTime: '18:00'
    },
    database: {
      host: 'neo4j',
      port: 7687,
      username: 'neo4j',
      password: 'password',
      database: 'stockmarket',
      backupSchedule: 'daily',
      backupTime: '00:00',
      maxBackups: 7,
      backupLocation: '/data/backups'
    },
    system: {
      dataRefreshInterval: 15,
      logLevel: 'info',
      enableDebugMode: false,
      cleanupOldDataAfter: 90,
      maxConcurrentRequests: 5
    }
  });

  const handleChange = (section, field, value) => {
    setSettings({
      ...settings,
      [section]: {
        ...settings[section],
        [field]: value
      }
    });
  };

  const handleSave = () => {
    // 실제 구현에서는 API 호출로 설정 저장
    console.log('Saving settings:', settings);
    
    setSnackbar({
      open: true,
      message: '설정이 저장되었습니다.',
      severity: 'success'
    });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({
      ...snackbar,
      open: false
    });
  };

  const handleOpenDialog = (type, data = {}) => {
    setDialogType(type);
    setDialogData(data);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setDialogData({});
  };

  const handleDialogSave = () => {
    // 실제 구현에서는 API 호출로 설정 저장
    console.log('Dialog save:', dialogType, dialogData);
    
    if (dialogType === 'telegram') {
      setSettings({
        ...settings,
        telegram: {
          ...settings.telegram,
          botToken: dialogData.botToken || settings.telegram.botToken,
          chatId: dialogData.chatId || settings.telegram.chatId
        }
      });
    } else if (dialogType === 'database') {
      setSettings({
        ...settings,
        database: {
          ...settings.database,
          host: dialogData.host || settings.database.host,
          port: dialogData.port || settings.database.port,
          username: dialogData.username || settings.database.username,
          password: dialogData.password || settings.database.password,
          database: dialogData.database || settings.database.database
        }
      });
    }
    
    setSnackbar({
      open: true,
      message: '설정이 업데이트되었습니다.',
      severity: 'success'
    });
    
    handleCloseDialog();
  };

  const handleDialogChange = (field, value) => {
    setDialogData({
      ...dialogData,
      [field]: value
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
        설정
      </Typography>
      
      <Grid container spacing={3}>
        {/* 텔레그램 설정 */}
        <Grid item xs={12}>
          <Card>
            <CardHeader 
              title="텔레그램 봇 설정" 
              avatar={<TelegramIcon color="primary" />}
              action={
                <Button
                  variant="outlined"
                  startIcon={<EditIcon />}
                  onClick={() => handleOpenDialog('telegram', {
                    botToken: settings.telegram.botToken,
                    chatId: settings.telegram.chatId
                  })}
                >
                  API 설정 편집
                </Button>
              }
            />
            <Divider />
            <CardContent>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.telegram.enabled}
                        onChange={(e) => handleChange('telegram', 'enabled', e.target.checked)}
                      />
                    }
                    label="텔레그램 봇 활성화"
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.telegram.notifyOnMarketOpen}
                        onChange={(e) => handleChange('telegram', 'notifyOnMarketOpen', e.target.checked)}
                        disabled={!settings.telegram.enabled}
                      />
                    }
                    label="시장 개장 시 알림"
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.telegram.notifyOnMarketClose}
                        onChange={(e) => handleChange('telegram', 'notifyOnMarketClose', e.target.checked)}
                        disabled={!settings.telegram.enabled}
                      />
                    }
                    label="시장 마감 시 알림"
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.telegram.notifyOnSignificantChange}
                        onChange={(e) => handleChange('telegram', 'notifyOnSignificantChange', e.target.checked)}
                        disabled={!settings.telegram.enabled}
                      />
                    }
                    label="중요 변동 시 알림"
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="중요 변동 기준 (%)"
                    type="number"
                    value={settings.telegram.significantChangeThreshold}
                    onChange={(e) => handleChange('telegram', 'significantChangeThreshold', e.target.value)}
                    disabled={!settings.telegram.enabled || !settings.telegram.notifyOnSignificantChange}
                    InputProps={{ inputProps: { min: 1, max: 20 } }}
                  />
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    label="일일 보고서 시간"
                    type="time"
                    value={settings.telegram.dailyReportTime}
                    onChange={(e) => handleChange('telegram', 'dailyReportTime', e.target.value)}
                    disabled={!settings.telegram.enabled}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <FormControl fullWidth disabled={!settings.telegram.enabled}>
                    <InputLabel>주간 보고서 요일</InputLabel>
                    <Select
                      value={settings.telegram.weeklyReportDay}
                      onChange={(e) => handleChange('telegram', 'weeklyReportDay', e.target.value)}
                      label="주간 보고서 요일"
                    >
                      <MenuItem value="monday">월요일</MenuItem>
                      <MenuItem value="tuesday">화요일</MenuItem>
                      <MenuItem value="wednesday">수요일</MenuItem>
                      <MenuItem value="thursday">목요일</MenuItem>
                      <MenuItem value="friday">금요일</MenuItem>
                      <MenuItem value="saturday">토요일</MenuItem>
                      <MenuItem value="sunday">일요일</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    label="주간 보고서 시간"
                    type="time"
                    value={settings.telegram.weeklyReportTime}
                    onChange={(e) => handleChange('telegram', 'weeklyReportTime', e.target.value)}
                    disabled={!settings.telegram.enabled}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="월간 보고서 일자"
                    type="number"
                    value={settings.telegram.monthlyReportDay}
                    onChange={(e) => handleChange('telegram', 'monthlyReportDay', e.target.value)}
                    disabled={!settings.telegram.enabled}
                    InputProps={{ inputProps: { min: 1, max: 28 } }}
                    helperText="매월 1-28일 중 선택"
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="월간 보고서 시간"
                    type="time"
                    value={settings.telegram.monthlyReportTime}
                    onChange={(e) => handleChange('telegram', 'monthlyReportTime', e.target.value)}
                    disabled={!settings.telegram.enabled}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        
        {/* 데이터베이스 설정 */}
        <Grid item xs={12}>
          <Card>
            <CardHeader 
              title="Neo4j 데이터베이스 설정" 
              avatar={<StorageIcon color="primary" />}
              action={
                <Button
                  variant="outlined"
                  startIcon={<EditIcon />}
                  onClick={() => handleOpenDialog('database', {
                    host: settings.database.host,
                    port: settings.database.port,
                    username: settings.database.username,
                    password: settings.database.password,
                    database: settings.database.database
                  })}
                >
                  연결 설정 편집
                </Button>
              }
            />
            <Divider />
            <CardContent>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>백업 주기</InputLabel>
                    <Select
                      value={settings.database.backupSchedule}
                      onChange={(e) => handleChange('database', 'backupSchedule', e.target.value)}
                      label="백업 주기"
                    >
                      <MenuItem value="hourly">매시간</MenuItem>
                      <MenuItem value="daily">매일</MenuItem>
                      <MenuItem value="weekly">매주</MenuItem>
                      <MenuItem value="monthly">매월</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="백업 시간"
                    type="time"
                    value={settings.database.backupTime}
                    onChange={(e) => handleChange('database', 'backupTime', e.target.value)}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="최대 백업 수"
                    type="number"
                    value={settings.database.maxBackups}
                    onChange={(e) => handleChange('database', 'maxBackups', e.target.value)}
                    InputProps={{ inputProps: { min: 1, max: 30 } }}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="백업 저장 위치"
                    value={settings.database.backupLocation}
                    onChange={(e) => handleChange('database', 'backupLocation', e.target.value)}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                    <Button
                      variant="outlined"
                      color="primary"
                      startIcon={<BackupIcon />}
                    >
                      지금 백업 실행
                    </Button>
                    
                    <Button
                      variant="outlined"
                      color="error"
                      startIcon={<DeleteIcon />}
                    >
                      데이터베이스 초기화
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        
        {/* 시스템 설정 */}
        <Grid item xs={12}>
          <Card>
            <CardHeader 
              title="시스템 설정" 
              avatar={<NotificationsIcon color="primary" />}
            />
            <Divider />
            <CardContent>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="데이터 갱신 주기 (분)"
                    type="number"
                    value={settings.system.dataRefreshInterval}
                    onChange={(e) => handleChange('system', 'dataRefreshInterval', e.target.value)}
                    InputProps={{ inputProps: { min: 1, max: 60 } }}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>로그 레벨</InputLabel>
                    <Select
                      value={settings.system.logLevel}
                      onChange={(e) => handleChange('system', 'logLevel', e.target.value)}
                      label="로그 레벨"
                    >
                      <MenuItem value="debug">Debug</MenuItem>
                      <MenuItem value="info">Info</MenuItem>
                      <MenuItem value="warning">Warning</MenuItem>
                      <MenuItem value="error">Error</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.system.enableDebugMode}
                        onChange={(e) => handleChange('system', 'enableDebugMode', e.target.checked)}
                      />
                    }
                    label="디버그 모드 활성화"
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="오래된 데이터 정리 기간 (일)"
                    type="number"
                    value={settings.system.cleanupOldDataAfter}
                    onChange={(e) => handleChange('system', 'cleanupOldDataAfter', e.target.value)}
                    InputProps={{ inputProps: { min: 30, max: 365 } }}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="최대 동시 요청 수"
                    type="number"
                    value={settings.system.maxConcurrentRequests}
                    onChange={(e) => handleChange('system', 'maxConcurrentRequests', e.target.value)}
                    InputProps={{ inputProps: { min: 1, max: 20 } }}
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        
        {/* 저장 버튼 */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
            <Button
              variant="contained"
              color="primary"
              onClick={handleSave}
              size="large"
              startIcon={<SaveIcon />}
            >
              모든 설정 저장
            </Button>
          </Box>
        </Grid>
      </Grid>
      
      {/* 텔레그램 설정 다이얼로그 */}
      <Dialog open={openDialog && dialogType === 'telegram'} onClose={handleCloseDialog}>
        <DialogTitle>텔레그램 봇 API 설정</DialogTitle>
        <DialogContent>
          <DialogContentText>
            텔레그램 봇 토큰과 채팅 ID를 입력하세요.
          </DialogContentText>
          
          <TextField
            margin="normal"
            label="봇 토큰"
            type="text"
            fullWidth
            value={dialogData.botToken || ''}
            onChange={(e) => handleDialogChange('botToken', e.target.value)}
          />
          
          <TextField
            margin="normal"
            label="채팅 ID"
            type="text"
            fullWidth
            value={dialogData.chatId || ''}
            onChange={(e) => handleDialogChange('chatId', e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>취소</Button>
          <Button onClick={handleDialogSave} variant="contained" color="primary">
            저장
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* 데이터베이스 설정 다이얼로그 */}
      <Dialog open={openDialog && dialogType === 'database'} onClose={handleCloseDialog}>
        <DialogTitle>Neo4j 데이터베이스 연결 설정</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Neo4j 데이터베이스 연결 정보를 입력하세요.
          </DialogContentText>
          
          <TextField
            margin="normal"
            label="호스트"
            type="text"
            fullWidth
            value={dialogData.host || ''}
            onChange={(e) => handleDialogChange('host', e.target.value)}
          />
          
          <TextField
            margin="normal"
            label="포트"
            type="number"
            fullWidth
            value={dialogData.port || ''}
            onChange={(e) => handleDialogChange('port', e.target.value)}
          />
          
          <TextField
            margin="normal"
            label="사용자명"
            type="text"
            fullWidth
            value={dialogData.username || ''}
            onChange={(e) => handleDialogChange('username', e.target.value)}
          />
          
          <TextField
            margin="normal"
            label="비밀번호"
            type="password"
            fullWidth
            value={dialogData.password || ''}
            onChange={(e) => handleDialogChange('password', e.target.value)}
          />
          
          <TextField
            margin="normal"
            label="데이터베이스"
            type="text"
            fullWidth
            value={dialogData.database || ''}
            onChange={(e) => handleDialogChange('database', e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>취소</Button>
          <Button onClick={handleDialogSave} variant="contained" color="primary">
            저장
          </Button>
        </DialogActions>
      </Dialog>
      
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

export default Settings;
