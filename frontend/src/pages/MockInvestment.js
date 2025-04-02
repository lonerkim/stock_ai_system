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
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  Tooltip
} from '@mui/material';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
} from 'chart.js';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import InfoIcon from '@mui/icons-material/Info';

// Chart.js 등록
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend
);

const MockInvestment = () => {
  const [loading, setLoading] = useState(true);
  const [portfolio, setPortfolio] = useState({
    initialCash: 100,
    cash: 0,
    totalValue: 0,
    roi: 0,
    positions: []
  });
  const [transactions, setTransactions] = useState([]);
  const [availableStocks, setAvailableStocks] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [transactionForm, setTransactionForm] = useState({
    type: 'buy',
    symbol: '',
    quantity: 1,
    price: 0
  });
  const [historyData, setHistoryData] = useState({
    labels: [],
    values: []
  });

  // 차트 데이터
  const chartData = {
    labels: historyData.labels,
    datasets: [
      {
        label: '포트폴리오 가치 ($)',
        data: historyData.values,
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
        text: '포트폴리오 가치 추이',
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
        // 포트폴리오 샘플 데이터
        const samplePortfolio = {
          initialCash: 100,
          cash: 42.35,
          totalValue: 128.72,
          roi: 28.72,
          positions: [
            { symbol: 'AAPL', name: 'Apple Inc.', quantity: 0.2, avgPrice: 178.50, currentPrice: 182.30, value: 36.46, roi: 2.13 },
            { symbol: 'MSFT', name: 'Microsoft Corp.', quantity: 0.1, avgPrice: 380.20, currentPrice: 385.50, value: 38.55, roi: 1.39 },
            { symbol: '005930', name: '삼성전자', quantity: 0.2, avgPrice: 72500, currentPrice: 73800, value: 11.36, roi: 1.79 }
          ]
        };
        
        // 거래 내역 샘플 데이터
        const sampleTransactions = [
          { id: 1, date: '2025-03-15', type: 'buy', symbol: 'AAPL', name: 'Apple Inc.', quantity: 0.2, price: 178.50, amount: 35.70 },
          { id: 2, date: '2025-03-18', type: 'buy', symbol: 'MSFT', name: 'Microsoft Corp.', quantity: 0.1, price: 380.20, amount: 38.02 },
          { id: 3, date: '2025-03-20', type: 'buy', symbol: '005930', name: '삼성전자', quantity: 0.2, price: 72500, amount: 11.15 },
          { id: 4, date: '2025-03-25', type: 'sell', symbol: 'AAPL', name: 'Apple Inc.', quantity: 0.1, price: 180.40, amount: 18.04 }
        ];
        
        // 사용 가능한 주식 샘플 데이터
        const sampleStocks = [
          { symbol: 'AAPL', name: 'Apple Inc.', price: 182.30 },
          { symbol: 'MSFT', name: 'Microsoft Corp.', price: 385.50 },
          { symbol: 'GOOGL', name: 'Alphabet Inc.', price: 142.56 },
          { symbol: 'AMZN', name: 'Amazon.com Inc.', price: 178.35 },
          { symbol: 'NVDA', name: 'NVIDIA Corp.', price: 875.28 },
          { symbol: '005930', name: '삼성전자', price: 73800 },
          { symbol: '000660', name: 'SK하이닉스', price: 138000 },
          { symbol: '035420', name: 'NAVER', price: 345000 },
          { symbol: '035720', name: '카카오', price: 98700 },
          { symbol: '051910', name: 'LG화학', price: 720000 }
        ];
        
        // 포트폴리오 가치 추이 샘플 데이터
        const today = new Date();
        const labels = [];
        const values = [];
        let value = 100;
        
        for (let i = 30; i >= 0; i--) {
          const date = new Date(today);
          date.setDate(date.getDate() - i);
          
          // 랜덤 변동 (-2% ~ +2%)
          const change = (Math.random() * 4 - 2) / 100;
          value = value * (1 + change);
          
          labels.push(date.toISOString().split('T')[0]);
          values.push(parseFloat(value.toFixed(2)));
        }
        
        setPortfolio(samplePortfolio);
        setTransactions(sampleTransactions);
        setAvailableStocks(sampleStocks);
        setHistoryData({ labels, values });
        setLoading(false);
      }, 1500);
    };

    fetchData();
  }, []);

  const handleOpenDialog = () => {
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setTransactionForm({
      type: 'buy',
      symbol: '',
      quantity: 1,
      price: 0
    });
  };

  const handleFormChange = (event) => {
    const { name, value } = event.target;
    
    setTransactionForm({
      ...transactionForm,
      [name]: value
    });
    
    // 주식 선택 시 현재 가격 자동 설정
    if (name === 'symbol') {
      const selectedStock = availableStocks.find(stock => stock.symbol === value);
      if (selectedStock) {
        setTransactionForm({
          ...transactionForm,
          symbol: value,
          price: selectedStock.price
        });
      }
    }
  };

  const handleTransaction = () => {
    // 실제 구현에서는 API 호출로 거래 실행
    console.log('Transaction:', transactionForm);
    
    // 거래 내역 추가 (시뮬레이션)
    const selectedStock = availableStocks.find(stock => stock.symbol === transactionForm.symbol);
    const newTransaction = {
      id: transactions.length + 1,
      date: new Date().toISOString().split('T')[0],
      type: transactionForm.type,
      symbol: transactionForm.symbol,
      name: selectedStock ? selectedStock.name : '',
      quantity: parseFloat(transactionForm.quantity),
      price: parseFloat(transactionForm.price),
      amount: parseFloat(transactionForm.quantity) * parseFloat(transactionForm.price)
    };
    
    setTransactions([newTransaction, ...transactions]);
    
    // 포트폴리오 업데이트 (시뮬레이션)
    let updatedPortfolio = { ...portfolio };
    
    if (transactionForm.type === 'buy') {
      // 매수 시 현금 감소
      updatedPortfolio.cash -= newTransaction.amount;
      
      // 포지션 업데이트
      const existingPosition = updatedPortfolio.positions.find(p => p.symbol === transactionForm.symbol);
      
      if (existingPosition) {
        // 기존 포지션 업데이트
        const totalQuantity = existingPosition.quantity + parseFloat(transactionForm.quantity);
        const totalCost = (existingPosition.quantity * existingPosition.avgPrice) + newTransaction.amount;
        const newAvgPrice = totalCost / totalQuantity;
        
        existingPosition.quantity = totalQuantity;
        existingPosition.avgPrice = newAvgPrice;
        existingPosition.value = totalQuantity * existingPosition.currentPrice;
        existingPosition.roi = ((existingPosition.currentPrice - newAvgPrice) / newAvgPrice) * 100;
      } else {
        // 새 포지션 추가
        updatedPortfolio.positions.push({
          symbol: transactionForm.symbol,
          name: selectedStock ? selectedStock.name : '',
          quantity: parseFloat(transactionForm.quantity),
          avgPrice: parseFloat(transactionForm.price),
          currentPrice: parseFloat(transactionForm.price),
          value: parseFloat(transactionForm.quantity) * parseFloat(transactionForm.price),
          roi: 0
        });
      }
    } else {
      // 매도 시 현금 증가
      updatedPortfolio.cash += newTransaction.amount;
      
      // 포지션 업데이트
      const existingPosition = updatedPortfolio.positions.find(p => p.symbol === transactionForm.symbol);
      
      if (existingPosition) {
        // 수량 감소
        existingPosition.quantity -= parseFloat(transactionForm.quantity);
        
        if (existingPosition.quantity <= 0) {
          // 포지션 제거
          updatedPortfolio.positions = updatedPortfolio.positions.filter(p => p.symbol !== transactionForm.symbol);
        } else {
          // 포지션 가치 업데이트
          existingPosition.value = existingPosition.quantity * existingPosition.currentPrice;
        }
      }
    }
    
    // 총 가치 및 ROI 업데이트
    const positionsValue = updatedPortfolio.positions.reduce((sum, position) => sum + position.value, 0);
    updatedPortfolio.totalValue = updatedPortfolio.cash + positionsValue;
    updatedPortfolio.roi = ((updatedPortfolio.totalValue - updatedPortfolio.initialCash) / updatedPortfolio.initialCash) * 100;
    
    setPortfolio(updatedPortfolio);
    handleCloseDialog();
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
        모의 투자
      </Typography>
      
      <Grid container spacing={3}>
        {/* 포트폴리오 요약 */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 140 }}>
            <Typography variant="h6" color="primary" gutterBottom>
              총 포트폴리오 가치
            </Typography>
            <Typography variant="h4" component="div" sx={{ flexGrow: 1 }}>
              ${portfolio.totalValue.toFixed(2)}
            </Typography>
            <Typography 
              variant="subtitle1" 
              color={portfolio.roi >= 0 ? 'success.main' : 'error.main'}
            >
              {portfolio.roi >= 0 ? '+' : ''}{portfolio.roi.toFixed(2)}% (${(portfolio.totalValue - portfolio.initialCash).toFixed(2)})
            </Typography>
          </Paper>
        </Grid>
        
        {/* 현금 잔액 */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 140 }}>
            <Typography variant="h6" color="primary" gutterBottom>
              현금 잔액
            </Typography>
            <Typography variant="h4" component="div" sx={{ flexGrow: 1 }}>
              ${portfolio.cash.toFixed(2)}
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              초기 투자금: ${portfolio.initialCash.toFixed(2)}
            </Typography>
          </Paper>
        </Grid>
        
        {/* 포지션 가치 */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 140 }}>
            <Typography variant="h6" color="primary" gutterBottom>
              포지션 가치
            </Typography>
            <Typography variant="h4" component="div" sx={{ flexGrow: 1 }}>
              ${(portfolio.totalValue - portfolio.cash).toFixed(2)}
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              보유 종목 수: {portfolio.positions.length}
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
        
        {/* 포지션 목록 */}
        <Grid item xs={12}>
          <Card>
            <CardHeader 
              title="보유 포지션" 
              action={
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<AddIcon />}
                  onClick={handleOpenDialog}
                >
                  거래 실행
                </Button>
              }
            />
            <Divider />
            <CardContent>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>심볼</TableCell>
                      <TableCell>종목명</TableCell>
                      <TableCell align="right">수량</TableCell>
                      <TableCell align="right">평균 매수가</TableCell>
                      <TableCell align="right">현재가</TableCell>
                      <TableCell align="right">평가금액</TableCell>
                      <TableCell align="right">수익률</TableCell>
                      <TableCell align="right">액션</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {portfolio.positions.length > 0 ? (
                      portfolio.positions.map((position) => (
                        <TableRow key={position.symbol}>
                          <TableCell>{position.symbol}</TableCell>
                          <TableCell>{position.name}</TableCell>
                          <TableCell align="right">{position.quantity.toFixed(2)}</TableCell>
                          <TableCell align="right">${position.avgPrice.toFixed(2)}</TableCell>
                          <TableCell align="right">${position.currentPrice.toFixed(2)}</TableCell>
                          <TableCell align="right">${position.value.toFixed(2)}</TableCell>
                          <TableCell 
                            align="right"
                            sx={{ color: position.roi >= 0 ? 'success.main' : 'error.main' }}
                          >
                            {position.roi >= 0 ? '+' : ''}{position.roi.toFixed(2)}%
                          </TableCell>
                          <TableCell align="right">
                            <Tooltip title="매도">
                              <IconButton 
                                size="small" 
                                color="error"
                                onClick={() => {
                                  setTransactionForm({
                                    type: 'sell',
                                    symbol: position.symbol,
                                    quantity: position.quantity,
                                    price: position.currentPrice
                                  });
                                  setOpenDialog(true);
                                }}
                              >
                                <RemoveIcon />
                              </IconButton>
                            </Tooltip>
                          </TableCell>
                        </TableRow>
                      ))
                    ) : (
                      <TableRow>
                        <TableCell colSpan={8} align="center">
                          보유 중인 포지션이 없습니다.
                        </TableCell>
                      </TableRow>
                    )}
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
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>날짜</TableCell>
                      <TableCell>유형</TableCell>
                      <TableCell>심볼</TableCell>
                      <TableCell>종목명</TableCell>
                      <TableCell align="right">수량</TableCell>
                      <TableCell align="right">가격</TableCell>
                      <TableCell align="right">금액</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {transactions.map((transaction) => (
                      <TableRow key={transaction.id}>
                        <TableCell>{transaction.date}</TableCell>
                        <TableCell>
                          <Chip 
                            label={transaction.type === 'buy' ? '매수' : '매도'} 
                            color={transaction.type === 'buy' ? 'primary' : 'error'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{transaction.symbol}</TableCell>
                        <TableCell>{transaction.name}</TableCell>
                        <TableCell align="right">{transaction.quantity.toFixed(2)}</TableCell>
                        <TableCell align="right">${transaction.price.toFixed(2)}</TableCell>
                        <TableCell align="right">${transaction.amount.toFixed(2)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      {/* 거래 다이얼로그 */}
      <Dialog open={openDialog} onClose={handleCloseDialog}>
        <DialogTitle>{transactionForm.type === 'buy' ? '매수 주문' : '매도 주문'}</DialogTitle>
        <DialogContent>
          <DialogContentText>
            {transactionForm.type === 'buy' 
              ? '매수할 종목과 수량을 입력하세요.' 
              : '매도할 수량을 입력하세요.'}
          </DialogContentText>
          
          <FormControl fullWidth margin="normal">
            <InputLabel>거래 유형</InputLabel>
            <Select
              name="type"
              value={transactionForm.type}
              onChange={handleFormChange}
              label="거래 유형"
            >
              <MenuItem value="buy">매수</MenuItem>
              <MenuItem value="sell">매도</MenuItem>
            </Select>
          </FormControl>
          
          <FormControl fullWidth margin="normal">
            <InputLabel>종목</InputLabel>
            <Select
              name="symbol"
              value={transactionForm.symbol}
              onChange={handleFormChange}
              label="종목"
              disabled={transactionForm.type === 'sell'}
            >
              {availableStocks.map((stock) => (
                <MenuItem key={stock.symbol} value={stock.symbol}>
                  {stock.symbol} - {stock.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <TextField
            margin="normal"
            name="quantity"
            label="수량"
            type="number"
            fullWidth
            value={transactionForm.quantity}
            onChange={handleFormChange}
            InputProps={{ inputProps: { min: 0.01, step: 0.01 } }}
          />
          
          <TextField
            margin="normal"
            name="price"
            label="가격 ($)"
            type="number"
            fullWidth
            value={transactionForm.price}
            onChange={handleFormChange}
            InputProps={{ inputProps: { min: 0.01, step: 0.01 } }}
          />
          
          <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
            <Typography variant="subtitle2" gutterBottom>
              주문 정보
            </Typography>
            <Typography variant="body2">
              총 금액: ${(transactionForm.quantity * transactionForm.price).toFixed(2)}
            </Typography>
            {transactionForm.type === 'buy' && (
              <Typography 
                variant="body2" 
                color={portfolio.cash >= (transactionForm.quantity * transactionForm.price) ? 'text.secondary' : 'error.main'}
              >
                주문 후 잔액: ${(portfolio.cash - (transactionForm.quantity * transactionForm.price)).toFixed(2)}
              </Typography>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>취소</Button>
          <Button 
            onClick={handleTransaction} 
            variant="contained" 
            color={transactionForm.type === 'buy' ? 'primary' : 'error'}
            disabled={
              transactionForm.symbol === '' || 
              transactionForm.quantity <= 0 || 
              transactionForm.price <= 0 ||
              (transactionForm.type === 'buy' && portfolio.cash < (transactionForm.quantity * transactionForm.price))
            }
          >
            {transactionForm.type === 'buy' ? '매수' : '매도'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MockInvestment;
