# Project: P407 

금융의 기술분석에서 기술적 지표는 과거 가격, 물량, 또는 (선물 계약의 경우) 개방형 이자정보에 근거한 수학적 계산으로 금융시장 방향 예측을 목적으로 한다. 기술지표는 기술분석의 기본적인 부분이며, 일반적으로 시장 동향을 예측하기 위해 차트 패턴으로 표시된다. 많은 기술적 지표가 개발되었고 더 나은 결과를 얻기 위해 거래자 혹은 연구자들에 의해 새로운 지표들이 계속 개발되고 있다.

## **주식 보조지표의 종류**

### **추세지표 : 주가가 진행하는 방향, 주가 추세를 알아보는 지표**

- 이동평균선, MACD, MACD 오실레이터, DMI, MAO, Privot Line, Parabolic Sar

 

### **변동성 지표 : 주가의 변동성을 알아보는 지표**

- ATR, 볼린저 밴드, Envelope, Keltner Channels

### **모멘텀 지표 : 투자심리나 운동에너지를 이용하여 주가 추세의 변곡점을 찾아보는 지표**

- 이격도, P&F, 투자심리선, 삼선전환도, AB Ratio, Maxx Index, Price 오실레이터, RSI, SONAR, TRIX

### **시장강도 지표**

- 거래량, OBV, 거래량 이동평균선, EOM, MFI, Volume 오실레이터, Volume Ratio

많은 혹은 대부분의 투자자들이 기술적 지표로 차트를 분석하고 매수 시점과 매도 시점을 파악하여 매매의 기준을 세우는데 활용한다. 여기서 매매의 기준들을 전략이라고 한다. 궁극적으로 우리가 알아내고자 하는 것은 이 ‘전략’을 어떤 종목에 대해 시험하고 수익률이 높은 종목을 발굴하는 것이다. 전략이 통하는 종목을 발굴함으로써 수익률을 극대화하고 안정화하는 것에 목적이 있다. 대표적으로 장기 이평선과 단기 이평선을 이용한 골든크로스, 데드크로스 전략이 있다.

현재 증권사 HTS나 기타 금융 서비스를 제공하는 회사들이 기술적 분석을 사용한 시뮬레이션 기능을 제공한다. 하지만 기능의 자유도가 떨어지고 많이 알려진 전략밖에 지원하지 않는다. 우리가 만들고자 하는 시스템에서는 전략에 적용할 수 있는 기술적 지표들을 확장이 필요할 때마다 추가할 수 있고 복잡한 조건도 지원한다. 파이썬 문법을 기초로 하고 있기 때문에 다중 if문 선언, 조건의 우선 순위 결정 등의 많은 기능들을 지원한다.


## **레이블러 종류**
## candles

- 캔들 종류(Candle Type): **candle_type**
- 캔들 모양(Candle Shape): **candle_shape**

## cross

- 이동평균 크로스(MA Cross): **ma_cross**
- 거래량가중이동평균 크로스(VWMA) Cross: **vwma_cross**
- 이동평균수렴확산지수 크로스(MACD Cross): **macd_cross**
- 패스트-스토캐스틱 크로스(Fast-Stochastic Cross): **stochf**
- 슬로우-스토캐스틱 크로스(Slow-Stochastic Cross): **stoch**

## Classification

- 적삼병(Three white soldiers): **three_red**
- 흑삼병(Three black crows): **three_blue**
- 볼린저 밴드(Bollinger Bands): **bbands**
