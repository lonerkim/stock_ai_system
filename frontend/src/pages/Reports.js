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
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  IconButton,
  Tooltip
} from '@mui/material';
import { Line, Bar, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
} from 'chart.js';
import DownloadIcon from '@mui/icons-material/Download';
import ShareIcon from '@mui/icons-material/Share';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';

// Chart.js 등록
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  ChartTooltip,
  Legend
);

const Reports = () => {
  const [loading, setLoading] = useState(true);
  const [tabValue, setTabValue] = useState(0);
  const [reportData, setReportData] = useState({
    daily: {},
    weekly: {},
    monthly: {}
  });

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // 데이터 로딩 시뮬레이션
  useEffect(() => {
    const fetchData = async () => {
      // 실제 구현에서는 API 호출로 대체
      setTimeout(() => {
        // 일일 보고서 샘플 데이터
        const dailyData = {
          date: '2025-04-01',
          summary: '오늘 포트폴리오는 1.2% 상승했습니다. 주요 상승 요인은 애플과 엔비디아의 강세였습니다.',
          portfolioValue: 128.72,
          previousValue: 127.20,
          change: 1.52,
          changePercent: 1.2,
          transactions: [
            { symbol: 'AAPL', name: 'Apple Inc.', type: 'buy', quantity: 0.1, price: 182.30, amount: 18.23 }
          ],
          topPerformers: [
            { symbol: 'AAPL', name: 'Apple Inc.', change: 2.1 },
            { symbol: 'NVDA', name: 'NVIDIA Corp.', change: 3.2 }
          ],
          worstPerformers: [
            { symbol: 'TSLA', name: 'Tesla Inc.', change: -1.5 },
            { symbol: 'AMZN', name: 'Amazon.com Inc.', change: -0.8 }
          ],
          marketSummary: {
            korean: '한국 시장은 전반적으로 상승세를 보였습니다.',
            us: '미국 시장은 기술주 중심으로 상승했습니다.'
          },
          performanceChart: {
            labels: ['9:30', '10:30', '11:30', '12:30', '13:30', '14:30', '15:30', '16:00'],
            values: [127.20, 127.45, 127.80, 128.10, 127.90, 128.30, 128.60, 128.72]
          },
          allocationChart: {
            labels: ['현금', 'AAPL', 'MSFT', '삼성전자'],
            values: [42.35, 36.46, 38.55, 11.36]
          }
        };
        
        // 주간 보고서 샘플 데이터
        const weeklyData = {
          startDate: '2025-03-24',
          endDate: '2025-04-01',
          summary: '이번 주 포트폴리오는 3.5% 상승했습니다. 주요 상승 요인은 기술주의 강세와 긍정적인 경제 지표였습니다.',
          portfolioValue: 128.72,
          previousValue: 124.37,
          change: 4.35,
          changePercent: 3.5,
          transactions: [
            { symbol: 'AAPL', name: 'Apple Inc.', type: 'buy', quantity: 0.1, price: 182.30, amount: 18.23 },
            { symbol: 'MSFT', name: 'Microsoft Corp.', type: 'buy', quantity: 0.05, price: 385.50, amount: 19.28 }
          ],
          topPerformers: [
            { symbol: 'AAPL', name: 'Apple Inc.', change: 4.2 },
            { symbol: 'NVDA', name: 'NVIDIA Corp.', change: 5.8 }
          ],
          worstPerformers: [
            { symbol: 'TSLA', name: 'Tesla Inc.', change: -2.3 },
            { symbol: 'AMZN', name: 'Amazon.com Inc.', change: -1.2 }
          ],
          marketSummary: {
            korean: '한국 시장은 이번 주 2.8% 상승했습니다.',
            us: '미국 시장은 이번 주 S&P 500 기준 1.9% 상승했습니다.'
          },
          performanceChart: {
            labels: ['3/24', '3/25', '3/26', '3/27', '3/28', '3/31', '4/1'],
            values: [124.37, 125.10, 125.80, 126.50, 127.20, 127.90, 128.72]
          },
          allocationChart: {
            labels: ['현금', 'AAPL', 'MSFT', '삼성전자'],
            values: [42.35, 36.46, 38.55, 11.36]
          },
          sectorPerformance: {
            labels: ['기술', '금융', '헬스케어', '소비재', '에너지'],
            values: [4.2, 2.1, 1.8, -0.5, -1.2]
          }
        };
        
        // 월간 보고서 샘플 데이터
        const monthlyData = {
          month: '2025-03',
          summary: '3월 포트폴리오는 12.8% 상승했습니다. 주요 상승 요인은 AI 관련 기술주의 강세와 금리 인하 기대감이었습니다.',
          portfolioValue: 128.72,
          previousValue: 114.11,
          change: 14.61,
          changePercent: 12.8,
          transactions: [
            { symbol: 'AAPL', name: 'Apple Inc.', type: 'buy', quantity: 0.2, price: 178.50, amount: 35.70 },
            { symbol: 'MSFT', name: 'Microsoft Corp.', type: 'buy', quantity: 0.1, price: 380.20, amount: 38.02 },
            { symbol: '005930', name: '삼성전자', type: 'buy', quantity: 0.2, price: 72500, amount: 11.15 },
            { symbol: 'AAPL', name: 'Apple Inc.', type: 'sell', quantity: 0.1, price: 180.40, amount: 18.04 }
          ],
          topPerformers: [
            { symbol: 'NVDA', name: 'NVIDIA Corp.', change: 18.5 },
            { symbol: 'AAPL', name: 'Apple Inc.', change: 8.2 },
            { symbol: 'MSFT', name: 'Microsoft Corp.', change: 6.5 }
          ],
          worstPerformers: [
            { symbol: 'TSLA', name: 'Tesla Inc.', change: -5.8 },
            { symbol: 'AMZN', name: 'Amazon.com Inc.', change: -2.3 }
          ],
          marketSummary: {
            korean: '한국 시장은 3월 KOSPI 기준 4.5% 상승했습니다.',
            us: '미국 시장은 3월 S&P 500 기준 3.8% 상승했습니다.'
          },
          performanceChart: {
            labels: ['3/1', '3/5', '3/10', '3/15', '3/20', '3/25', '4/1'],
            values: [114.11, 116.50, 119.80, 122.30, 124.70, 127.20, 128.72]
          },
          allocationChart: {
            labels: ['현금', 'AAPL', 'MSFT', '삼성전자'],
            values: [42.35, 36.46, 38.55, 11.36]
          },
          sectorPerformance: {
            labels: ['기술', '금융', '헬스케어', '소비재', '에너지'],
            values: [15.2, 8.1, 5.8, 2.5, -3.2]
          },
          monthlyComparison: {
            labels: ['1월', '2월', '3월'],
            values: [3.2, 5.5, 12.8]
          }
        };
        
        setReportData({
          daily: dailyData,
          weekly: weeklyData,
          monthly: monthlyData
        });
        
        setLoading(false);
      }, 1500);
    };

    fetchData();
  }, []);

  // 현재 선택된 보고서 데이터
  const currentReport = tabValue === 0 ? reportData.daily : tabValue === 1 ? reportData.weekly : reportData.monthly;

  // 성과 차트 데이터
  const performanceChartData = {
    labels: currentReport.performanceChart?.labels || [],
    datasets: [
      {
        label: '포트폴리오 가치 ($)',
        data: currentReport.performanceChart?.values || [],
        fill: false,
        backgroundColor: 'rgba(75,192,192,0.4)',
        borderColor: 'rgba(75,192,192,1)',
      },
    ],
  };

  // 자산 배분 차트 데이터
  const allocationChartData = {
    labels: currentReport.allocationChart?.labels || [],
    datasets: [
      {
        label: '자산 배분',
        data: currentReport.allocationChart?.values || [],
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(153, 102, 255, 0.6)',
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  // 섹터 성과 차트 데이터 (주간 및 월간 보고서용)
  const sectorPerformanceChartData = {
    labels: currentReport.sectorPerformance?.labels || [],
    datasets: [
      {
        label: '섹터별 성과 (%)',
        data: currentReport.sectorPerformance?.values || [],
        backgroundColor: [
          'rgba(75, 192, 192, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(255, 99, 132, 0.6)',
          'rgba(153, 102, 255, 0.6)',
        ],
        borderColor: [
          'rgba(75, 192, 192, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(255, 99, 132, 1)',
          'rgba(153, 102, 255, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  // 월별 비교 차트 데이터 (월간 보고서용)
  const monthlyComparisonChartData = {
    labels: currentReport.monthlyComparison?.labels || [],
    datasets: [
      {
        label: '월별 수익률 (%)',
        data: currentReport.monthlyComparison?.values || [],
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
      },
    ],
  };

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
        보고서
      </Typography>
      
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="report tabs">
          <Tab label="일일 보고서" icon={<CalendarTodayIcon />} iconPosition="start" />
          <Tab label="주간 보고서" icon={<CalendarTodayIcon />} iconPosition="start" />
          <Tab label="월간 보고서" icon={<CalendarTodayIcon />} iconPosition="start" />
        </Tabs>
      </Box>
      
      <Grid container spacing={3}>
        {/* 보고서 헤더 */}
        <Grid item xs={12}>
          <Card>
            <CardHeader 
              title={
                tabValue === 0 ? `일일 보고서 (${currentReport.date})` : 
                tabValue === 1 ? `주간 보고서 (${currentReport.startDate} ~ ${currentReport.endDate})` :
                `월간 보고서 (${currentReport.month})`
              }
              action={
                <Box>
                  <Tooltip title="보고서 다운로드">
                    <IconButton>
                      <DownloadIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="보고서 공유">
                    <IconButton>
                      <ShareIcon />
                    </IconButton>
                  </Tooltip>
                </Box>
              }
            />
            <Divider />
            <CardContent>
              <Typography variant="body1" paragraph>
                {currentReport.summary}
              </Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={12} md={3}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="subtitle2" color="text.secondary">현재 가치</Typography>
                    <Typography variant="h5">${currentReport.portfolioValue?.toFixed(2)}</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="subtitle2" color="text.secondary">이전 가치</Typography>
                    <Typography variant="h5">${currentReport.previousValue?.toFixed(2)}</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="subtitle2" color="text.secondary">변동액</Typography>
                    <Typography variant="h5" color={currentReport.change >= 0 ? 'success.main' : 'error.main'}>
                      {currentReport.change >= 0 ? '+' : ''}${currentReport.change?.toFixed(2)}
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="subtitle2" color="text.secondary">변동률</Typography>
                    <Typography variant="h5" color={currentReport.changePercent >= 0 ? 'success.main' : 'error.main'}>
                      {currentReport.changePercent >= 0 ? '+' : ''}{currentReport.changePercent?.toFixed(2)}%
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        
        {/* 성과 차트 */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardHeader title="포트폴리오 성과" />
            <Divider />
            <CardContent>
              <Box sx={{ height: 300 }}>
                <Line data={performanceChartData} options={{ maintainAspectRatio: false }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        {/* 자산 배분 차트 */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader title="자산 배분" />
            <Divider />
            <CardContent>
              <Box sx={{ height: 300 }}>
                <Pie data={allocationChartData} options={{ maintainAspectRatio: false }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        {/* 시장 요약 */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="시장 요약" />
            <Divider />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1" gutterBottom>한국 시장</Typography>
                  <Typography variant="body1">{currentReport.marketSummary?.korean}</Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1" gutterBottom>미국 시장</Typography>
                  <Typography variant="body1">{currentReport.marketSummary?.us}</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        
        {/* 상위/하위 종목 */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="상위 종목" />
            <Divider />
            <CardContent>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>심볼</TableCell>
                      <TableCell>종목명</TableCell>
                      <TableCell align="right">변동률</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {currentReport.topPerformers?.map((stock) => (
                      <TableRow key={stock.symbol}>
                        <TableCell>{stock.symbol}</TableCell>
                        <TableCell>{stock.name}</TableCell>
                        <TableCell align="right" sx={{ color: 'success.main' }}>
                          +{stock.change}%
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="하위 종목" />
            <Divider />
            <CardContent>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>심볼</TableCell>
                      <TableCell>종목명</TableCell>
                      <TableCell align="right">변동률</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {currentReport.worstPerformers?.map((stock) => (
                      <TableRow key={stock.symbol}>
                        <TableCell>{stock.symbol}</TableCell>
                        <TableCell>{stock.name}</TableCell>
                        <TableCell align="right" sx={{ color: 'error.main' }}>
                          {stock.change}%
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
        
        {/* 거래 내역 */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="거래 내역" />
            <Divider />
            <CardContent>
              {currentReport.transactions?.length > 0 ? (
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>심볼</TableCell>
                        <TableCell>종목명</TableCell>
                        <TableCell>유형</TableCell>
                        <TableCell align="right">수량</TableCell>
                        <TableCell align="right">가격</TableCell>
                        <TableCell align="right">금액</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {currentReport.transactions.map((transaction, index) => (
                        <TableRow key={index}>
                          <TableCell>{transaction.symbol}</TableCell>
                          <TableCell>{transaction.name}</TableCell>
                          <TableCell>{transaction.type === 'buy' ? '매수' : '매도'}</TableCell>
                          <TableCell align="right">{transaction.quantity}</TableCell>
                          <TableCell align="right">${transaction.price}</TableCell>
                          <TableCell align="right">${transaction.amount}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography variant="body1" align="center">
                  거래 내역이 없습니다.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
        
        {/* 주간 및 월간 보고서에만 표시되는 섹터 성과 */}
        {(tabValue === 1 || tabValue === 2) && currentReport.sectorPerformance && (
          <Grid item xs={12}>
            <Card>
              <CardHeader title="섹터별 성과" />
              <Divider />
              <CardContent>
                <Box sx={{ height: 300 }}>
                  <Bar data={sectorPerformanceChartData} options={{ maintainAspectRatio: false }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}
        
        {/* 월간 보고서에만 표시되는 월별 비교 */}
        {tabValue === 2 && currentReport.monthlyComparison && (
          <Grid item xs={12}>
            <Card>
              <CardHeader title="월별 수익률 비교" />
              <Divider />
              <CardContent>
                <Box sx={{ height: 300 }}>
                  <Bar data={monthlyComparisonChartData} options={{ maintainAspectRatio: false }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}
        
        {/* 텔레그램으로 보고서 전송 버튼 */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
            <Button
              variant="contained"
              color="primary"
              size="large"
              startIcon={<ShareIcon />}
            >
              텔레그램으로 보고서 전송
            </Button>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Reports;
