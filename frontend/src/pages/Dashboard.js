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
  Divider
} from '@mui/material';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Chart.js 등록
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [marketData, setMarketData] = useState({
    korean: { summary: '', trend: '' },
    us: { summary: '', trend: '' }
  });
  const [portfolioData, setPortfolioData] = useState({
    initialValue: 100,
    currentValue: 0,
    roi: 0,
    history: []
  });

  // 차트 데이터
  const chartData = {
    labels: portfolioData.history.map(item => item.date),
    datasets: [
      {
        label: '포트폴리오 가치 ($)',
        data: portfolioData.history.map(item => item.value),
        fill: false,
        backgroundColor: 'rgba(75,192,192,0.4)',
        borderColor: 'rgba(75,192,192,1)',
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: '모의 투자 성과',
      },
    },
    scales: {
      y: {
        beginAtZero: false,
      },
    },
  };

  // 데이터 로딩 시뮬레이션
  useEffect(() => {
    const fetchData = async () => {
      // 실제 구현에서는 API 호출로 대체
      setTimeout(() => {
        setMarketData({
          korean: { 
            summary: '한국 시장은 최근 기술주를 중심으로 상승세를 보이고 있습니다.', 
            trend: '상승' 
          },
          us: { 
            summary: '미국 시장은 인플레이션 우려로 인해 변동성이 커지고 있습니다.', 
            trend: '혼조' 
          }
        });
        
        // 샘플 포트폴리오 데이터
        const today = new Date();
        const history = [];
        let value = 100;
        
        for (let i = 30; i >= 0; i--) {
          const date = new Date(today);
          date.setDate(date.getDate() - i);
          
          // 랜덤 변동 (-3% ~ +3%)
          const change = (Math.random() * 6 - 3) / 100;
          value = value * (1 + change);
          
          history.push({
            date: date.toISOString().split('T')[0],
            value: parseFloat(value.toFixed(2))
          });
        }
        
        setPortfolioData({
          initialValue: 100,
          currentValue: parseFloat(value.toFixed(2)),
          roi: parseFloat(((value - 100) / 100 * 100).toFixed(2)),
          history
        });
        
        setLoading(false);
      }, 1500);
    };

    fetchData();
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
        대시보드
      </Typography>
      
      <Grid container spacing={3}>
        {/* 포트폴리오 요약 */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 140 }}>
            <Typography variant="h6" color="primary" gutterBottom>
              모의 투자 포트폴리오
            </Typography>
            <Typography variant="h4" component="div" sx={{ flexGrow: 1 }}>
              ${portfolioData.currentValue}
            </Typography>
            <Typography 
              variant="subtitle1" 
              color={portfolioData.roi >= 0 ? 'success.main' : 'error.main'}
            >
              {portfolioData.roi >= 0 ? '+' : ''}{portfolioData.roi}% (${(portfolioData.currentValue - portfolioData.initialValue).toFixed(2)})
            </Typography>
          </Paper>
        </Grid>
        
        {/* 한국 시장 요약 */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 140 }}>
            <Typography variant="h6" color="primary" gutterBottom>
              한국 시장
            </Typography>
            <Typography variant="body1" sx={{ flexGrow: 1 }}>
              {marketData.korean.summary}
            </Typography>
            <Typography 
              variant="subtitle1" 
              color={marketData.korean.trend === '상승' ? 'success.main' : marketData.korean.trend === '하락' ? 'error.main' : 'text.secondary'}
            >
              트렌드: {marketData.korean.trend}
            </Typography>
          </Paper>
        </Grid>
        
        {/* 미국 시장 요약 */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 140 }}>
            <Typography variant="h6" color="primary" gutterBottom>
              미국 시장
            </Typography>
            <Typography variant="body1" sx={{ flexGrow: 1 }}>
              {marketData.us.summary}
            </Typography>
            <Typography 
              variant="subtitle1" 
              color={marketData.us.trend === '상승' ? 'success.main' : marketData.us.trend === '하락' ? 'error.main' : 'text.secondary'}
            >
              트렌드: {marketData.us.trend}
            </Typography>
          </Paper>
        </Grid>
        
        {/* 포트폴리오 차트 */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Box sx={{ height: 300 }}>
              <Line data={chartData} options={chartOptions} />
            </Box>
          </Paper>
        </Grid>
        
        {/* 최근 AI 분석 */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="최근 AI 분석 결과" />
            <Divider />
            <CardContent>
              <Typography variant="body1" paragraph>
                최근 시장 분석에 따르면, 기술 섹터와 헬스케어 섹터가 강세를 보이고 있습니다. 특히 반도체 관련 주식들이 공급망 개선과 AI 수요 증가로 인해 상승세를 유지하고 있습니다.
              </Typography>
              <Typography variant="body1">
                단기적으로는 중앙은행의 금리 정책과 인플레이션 지표를 주시할 필요가 있으며, 장기 투자자들에게는 기술, 헬스케어, 그리고 지속 가능한 에너지 섹터의 블루칩 주식들이 매력적인 옵션으로 보입니다.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
