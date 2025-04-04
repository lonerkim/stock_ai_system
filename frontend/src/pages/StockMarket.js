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
  IconButton,
  Alert
} from '@mui/material';
import { marketApi } from '../services/api';
import SearchIcon from '@mui/icons-material/Search';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import TrendingFlatIcon from '@mui/icons-material/TrendingFlat';

// API 서비스 사용

const StockMarket = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
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
            return {
              summary_text: '한국 시장 데이터를 가져오는 중 오류가 발생했습니다.',
              top_stocks: []
            };
          });

        // 미국 시장 데이터 가져오기
        const usMarketData = await marketApi.getMarketOverview('us')
          .catch(err => {
            console.error('미국 시장 데이터 가져오기 실패:', err);
            return {
              summary_text: '미국 시장 데이터를 가져오는 중 오류가 발생했습니다.',
              top_stocks: []
            };
          });

        // 시장 데이터 형식 변환
        const formatStocks = (marketData) => {
          if (!marketData.top_stocks) return [];

          return marketData.top_stocks.map(stock => ({
            symbol: stock.symbol,
            name: stock.name,
            price: stock.latest_close || stock.price,
            change: stock.change_percent || 0,
            volume: stock.volume || 0
          }));
        };

        // 시장 데이터 설정
        setMarketData({
          korean: {
            summary: koreanMarketData.summary_text || '데이터 없음',
            stocks: formatStocks(koreanMarketData)
          },
          us: {
            summary: usMarketData.summary_text || '데이터 없음',
            stocks: formatStocks(usMarketData)
          }
        });

        setLoading(false);
      } catch (error) {
        console.error('데이터 가져오기 실패:', error);
        setError('데이터를 가져오는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
        setLoading(false);
      }
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
