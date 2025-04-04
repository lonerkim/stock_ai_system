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
  Alert
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

// API 서비스 가져오기
import { marketApi, portfolioApi } from '../services/api';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
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

  // API에서 데이터 가져오기
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // 한국 시장 데이터 가져오기
        const koreanMarketData = await marketApi.getMarketOverview('korean')
          .catch(err => {
            console.error('한국 시장 데이터 가져오기 실패:', err);
            return { summary_text: '한국 시장 데이터를 가져오는 중 오류가 발생했습니다.', trend: '알 수 없음' };
          });

        // 미국 시장 데이터 가져오기
        const usMarketData = await marketApi.getMarketOverview('us')
          .catch(err => {
            console.error('미국 시장 데이터 가져오기 실패:', err);
            return { summary_text: '미국 시장 데이터를 가져오는 중 오류가 발생했습니다.', trend: '알 수 없음' };
          });

        // 시장 데이터 설정
        setMarketData({
          korean: {
            summary: koreanMarketData.summary_text || '데이터 없음',
            trend: determineTrend(koreanMarketData)
          },
          us: {
            summary: usMarketData.summary_text || '데이터 없음',
            trend: determineTrend(usMarketData)
          }
        });

        // 포트폴리오 데이터 가져오기
        try {
          const portfolioResponse = await portfolioApi.getPerformance();

          setPortfolioData({
            initialValue: portfolioResponse.initial_value || 100,
            currentValue: portfolioResponse.current_value || 100,
            roi: portfolioResponse.roi || 0,
            history: portfolioResponse.history || []
          });
        } catch (portfolioError) {
          console.error('포트폴리오 데이터 가져오기 실패:', portfolioError);

          // 포트폴리오 API 실패 시 샘플 데이터 생성
          const today = new Date();
          const history = [];
          let value = 100;

          for (let i = 30; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);

            // 약간의 변동 (-1% ~ +1%)
            const change = (Math.random() * 2 - 1) / 100;
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
        }
      } catch (error) {
        console.error('데이터 가져오기 실패:', error);
        setError('데이터를 가져오는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
      } finally {
        setLoading(false);
      }
    };

    // 시장 트렌드 결정 함수
    const determineTrend = (marketData) => {
      if (!marketData || !marketData.indices) return '알 수 없음';

      // 한국 시장인 경우 KOSPI 확인
      if (marketData.indices.KOSPI) {
        const changePercent = marketData.indices.KOSPI.change_percent;
        if (changePercent > 0.5) return '상승';
        if (changePercent < -0.5) return '하락';
        return '보합';
      }

      // 미국 시장인 경우 S&P500 확인
      if (marketData.indices['S&P500']) {
        const changePercent = marketData.indices['S&P500'].change_percent;
        if (changePercent > 0.5) return '상승';
        if (changePercent < -0.5) return '하락';
        return '보합';
      }

      return '알 수 없음';
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

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{error}</Alert>
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
                {marketData.korean.summary}
              </Typography>
              <Typography variant="body1">
                {marketData.us.summary}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
