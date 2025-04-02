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
  TextField,
  InputAdornment,
  IconButton
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import TrendingFlatIcon from '@mui/icons-material/TrendingFlat';

const StockMarket = () => {
  const [loading, setLoading] = useState(true);
  const [tabValue, setTabValue] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [marketData, setMarketData] = useState({
    korean: {
      summary: '',
      stocks: []
    },
    us: {
      summary: '',
      stocks: []
    }
  });

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };

  // 데이터 로딩 시뮬레이션
  useEffect(() => {
    const fetchData = async () => {
      // 실제 구현에서는 API 호출로 대체
      setTimeout(() => {
        // 한국 주식 샘플 데이터
        const koreanStocks = [
          { symbol: '005930', name: '삼성전자', price: 72800, change: 1.2, volume: 12345678 },
          { symbol: '000660', name: 'SK하이닉스', price: 138000, change: 2.5, volume: 5678901 },
          { symbol: '035420', name: 'NAVER', price: 345000, change: -0.8, volume: 2345678 },
          { symbol: '035720', name: '카카오', price: 98700, change: -1.5, volume: 3456789 },
          { symbol: '051910', name: 'LG화학', price: 720000, change: 3.2, volume: 1234567 },
          { symbol: '207940', name: '삼성바이오로직스', price: 850000, change: 0.5, volume: 987654 },
          { symbol: '005380', name: '현대자동차', price: 210000, change: 1.8, volume: 2345678 },
          { symbol: '035900', name: 'JYP Ent.', price: 125000, change: 4.2, volume: 3456789 },
          { symbol: '373220', name: 'LG에너지솔루션', price: 450000, change: 2.1, volume: 1234567 },
          { symbol: '000270', name: '기아', price: 92000, change: 1.5, volume: 2345678 }
        ];

        // 미국 주식 샘플 데이터
        const usStocks = [
          { symbol: 'AAPL', name: 'Apple Inc.', price: 178.72, change: 1.5, volume: 45678901 },
          { symbol: 'MSFT', name: 'Microsoft Corp.', price: 380.45, change: 0.8, volume: 23456789 },
          { symbol: 'GOOGL', name: 'Alphabet Inc.', price: 142.56, change: -0.5, volume: 12345678 },
          { symbol: 'AMZN', name: 'Amazon.com Inc.', price: 178.35, change: 2.1, volume: 34567890 },
          { symbol: 'NVDA', name: 'NVIDIA Corp.', price: 875.28, change: 3.2, volume: 56789012 },
          { symbol: 'META', name: 'Meta Platforms Inc.', price: 485.92, change: 1.8, volume: 23456789 },
          { symbol: 'TSLA', name: 'Tesla Inc.', price: 172.63, change: -2.5, volume: 45678901 },
          { symbol: 'BRK.A', name: 'Berkshire Hathaway Inc.', price: 621450.00, change: 0.3, volume: 123456 },
          { symbol: 'JPM', name: 'JPMorgan Chase & Co.', price: 198.45, change: 0.7, volume: 12345678 },
          { symbol: 'V', name: 'Visa Inc.', price: 275.82, change: 0.5, volume: 9876543 }
        ];

        setMarketData({
          korean: {
            summary: '한국 시장은 최근 반도체와 2차전지 관련주를 중심으로 상승세를 보이고 있습니다. 특히 삼성전자와 SK하이닉스는 글로벌 AI 수요 증가에 따른 메모리 반도체 가격 상승 기대감으로 강세를 보이고 있습니다. 또한 LG에너지솔루션과 LG화학 등 2차전지 관련주도 전기차 시장 확대에 따른 수혜로 상승세를 이어가고 있습니다.',
            stocks: koreanStocks
          },
          us: {
            summary: '미국 시장은 기술주를 중심으로 상승세를 유지하고 있습니다. 특히 엔비디아를 비롯한 AI 관련주들이 강세를 보이고 있으며, 애플과 마이크로소프트 등 대형 기술주들도 견조한 실적을 바탕으로 상승세를 이어가고 있습니다. 다만 인플레이션 우려와 금리 인상 가능성으로 인해 시장 변동성이 확대될 수 있어 주의가 필요합니다.',
            stocks: usStocks
          }
        });
        
        setLoading(false);
      }, 1500);
    };

    fetchData();
  }, []);

  // 검색 필터링
  const filteredStocks = tabValue === 0 
    ? marketData.korean.stocks.filter(stock => 
        stock.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
        stock.symbol.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : marketData.us.stocks.filter(stock => 
        stock.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
        stock.symbol.toLowerCase().includes(searchTerm.toLowerCase())
      );

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
        주식 시장
      </Typography>
      
      <Grid container spacing={3}>
        {/* 시장 요약 */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title={tabValue === 0 ? "한국 시장 요약" : "미국 시장 요약"} />
            <Divider />
            <CardContent>
              <Typography variant="body1">
                {tabValue === 0 ? marketData.korean.summary : marketData.us.summary}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        {/* 주식 목록 */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
              <Tabs value={tabValue} onChange={handleTabChange} aria-label="market tabs">
                <Tab label="한국 시장" />
                <Tab label="미국 시장" />
              </Tabs>
            </Box>
            
            <Box sx={{ mb: 2 }}>
              <TextField
                fullWidth
                variant="outlined"
                placeholder="종목명 또는 심볼로 검색"
                value={searchTerm}
                onChange={handleSearchChange}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
              />
            </Box>
            
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>심볼</TableCell>
                    <TableCell>종목명</TableCell>
                    <TableCell align="right">가격</TableCell>
                    <TableCell align="right">변동률</TableCell>
                    <TableCell align="right">거래량</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredStocks.map((stock) => (
                    <TableRow key={stock.symbol}>
                      <TableCell>{stock.symbol}</TableCell>
                      <TableCell>{stock.name}</TableCell>
                      <TableCell align="right">
                        {tabValue === 0 ? `${stock.price.toLocaleString()}원` : `$${stock.price.toLocaleString()}`}
                      </TableCell>
                      <TableCell 
                        align="right"
                        sx={{ 
                          color: stock.change > 0 ? 'success.main' : stock.change < 0 ? 'error.main' : 'text.secondary',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'flex-end'
                        }}
                      >
                        {stock.change > 0 ? <TrendingUpIcon fontSize="small" sx={{ mr: 0.5 }} /> : 
                         stock.change < 0 ? <TrendingDownIcon fontSize="small" sx={{ mr: 0.5 }} /> : 
                         <TrendingFlatIcon fontSize="small" sx={{ mr: 0.5 }} />}
                        {stock.change > 0 ? '+' : ''}{stock.change}%
                      </TableCell>
                      <TableCell align="right">{stock.volume.toLocaleString()}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default StockMarket;
