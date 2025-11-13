/**
 * Advanced Trading Chart Component
 * Interactive candlestick and line charts with indicators
 */
import React, { useState } from 'react';
import { View, StyleSheet, Dimensions, ScrollView, TouchableOpacity, Text } from 'react-native';
import { LineChart, CandlestickChart } from 'react-native-chart-kit';
import { useTheme } from '../context/ThemeContext';

interface ChartData {
  labels: string[];
  datasets: Array<{
    data: number[];
    color?: (opacity: number) => string;
    strokeWidth?: number;
  }>;
}

interface CandleData {
  shadowH: number;
  shadowL: number;
  open: number;
  close: number;
}

interface AdvancedChartProps {
  data: ChartData;
  candleData?: CandleData[];
  title?: string;
  showIndicators?: boolean;
}

export const AdvancedChart: React.FC<AdvancedChartProps> = ({
  data,
  candleData,
  title,
  showIndicators = true,
}) => {
  const { colors, isDark } = useTheme();
  const [chartType, setChartType] = useState<'line' | 'candle'>('line');
  const [timeframe, setTimeframe] = useState<'1H' | '4H' | '1D' | '1W'>('1H');
  const [showVolume, setShowVolume] = useState(false);

  const screenWidth = Dimensions.get('window').width;

  const chartConfig = {
    backgroundColor: colors.surface,
    backgroundGradientFrom: colors.surface,
    backgroundGradientTo: colors.surface,
    decimalPlaces: 2,
    color: (opacity = 1) => `rgba(102, 126, 234, ${opacity})`,
    labelColor: (opacity = 1) => isDark
      ? `rgba(255, 255, 255, ${opacity * 0.7})`
      : `rgba(0, 0, 0, ${opacity * 0.7})`,
    style: {
      borderRadius: 16,
    },
    propsForDots: {
      r: '4',
      strokeWidth: '2',
      stroke: colors.primary,
    },
  };

  const renderLineChart = () => (
    <LineChart
      data={data}
      width={screenWidth - 40}
      height={220}
      chartConfig={chartConfig}
      bezier
      style={styles.chart}
      withInnerLines={true}
      withOuterLines={true}
      withVerticalLabels={true}
      withHorizontalLabels={true}
      withDots={data.labels.length < 20}
      withShadow={false}
      fromZero={false}
    />
  );

  const renderCandlestickChart = () => {
    if (!candleData || candleData.length === 0) {
      return renderLineChart();
    }

    return (
      <View style={styles.candleContainer}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <View style={styles.candleChart}>
            {candleData.map((candle, index) => {
              const isGreen = candle.close > candle.open;
              const bodyHeight = Math.abs(candle.close - candle.open);
              const wickTop = candle.shadowH - Math.max(candle.open, candle.close);
              const wickBottom = Math.min(candle.open, candle.close) - candle.shadowL;

              return (
                <View key={index} style={styles.candleWrapper}>
                  {/* Upper wick */}
                  <View
                    style={[
                      styles.wick,
                      {
                        height: wickTop * 2,
                        backgroundColor: isGreen ? colors.success : colors.error,
                      },
                    ]}
                  />
                  {/* Body */}
                  <View
                    style={[
                      styles.candleBody,
                      {
                        height: bodyHeight * 2,
                        backgroundColor: isGreen ? colors.success : colors.error,
                      },
                    ]}
                  />
                  {/* Lower wick */}
                  <View
                    style={[
                      styles.wick,
                      {
                        height: wickBottom * 2,
                        backgroundColor: isGreen ? colors.success : colors.error,
                      },
                    ]}
                  />
                </View>
              );
            })}
          </View>
        </ScrollView>
      </View>
    );
  };

  return (
    <View style={[styles.container, { backgroundColor: colors.surface }]}>
      {title && <Text style={[styles.title, { color: colors.text }]}>{title}</Text>}

      {/* Chart Type Selector */}
      <View style={styles.controls}>
        <View style={styles.buttonGroup}>
          <TouchableOpacity
            style={[
              styles.button,
              chartType === 'line' && { backgroundColor: colors.primary },
            ]}
            onPress={() => setChartType('line')}
          >
            <Text
              style={[
                styles.buttonText,
                { color: chartType === 'line' ? '#fff' : colors.text },
              ]}
            >
              Line
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[
              styles.button,
              chartType === 'candle' && { backgroundColor: colors.primary },
            ]}
            onPress={() => setChartType('candle')}
          >
            <Text
              style={[
                styles.buttonText,
                { color: chartType === 'candle' ? '#fff' : colors.text },
              ]}
            >
              Candle
            </Text>
          </TouchableOpacity>
        </View>

        {/* Timeframe Selector */}
        <View style={styles.buttonGroup}>
          {(['1H', '4H', '1D', '1W'] as const).map((tf) => (
            <TouchableOpacity
              key={tf}
              style={[
                styles.smallButton,
                timeframe === tf && { backgroundColor: colors.primary },
              ]}
              onPress={() => setTimeframe(tf)}
            >
              <Text
                style={[
                  styles.buttonText,
                  { color: timeframe === tf ? '#fff' : colors.text },
                ]}
              >
                {tf}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Chart */}
      <View style={styles.chartContainer}>
        {chartType === 'line' ? renderLineChart() : renderCandlestickChart()}
      </View>

      {/* Indicators */}
      {showIndicators && (
        <View style={styles.indicators}>
          <View style={styles.indicator}>
            <Text style={[styles.indicatorLabel, { color: colors.textSecondary }]}>
              RSI
            </Text>
            <Text style={[styles.indicatorValue, { color: colors.success }]}>65.4</Text>
          </View>
          <View style={styles.indicator}>
            <Text style={[styles.indicatorLabel, { color: colors.textSecondary }]}>
              MACD
            </Text>
            <Text style={[styles.indicatorValue, { color: colors.error }]}>-0.23</Text>
          </View>
          <View style={styles.indicator}>
            <Text style={[styles.indicatorLabel, { color: colors.textSecondary }]}>
              Volume
            </Text>
            <Text style={[styles.indicatorValue, { color: colors.text }]}>1.2M</Text>
          </View>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    borderRadius: 16,
    padding: 16,
    marginVertical: 8,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  controls: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  buttonGroup: {
    flexDirection: 'row',
    gap: 8,
  },
  button: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: 'rgba(102, 126, 234, 0.1)',
  },
  smallButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
    backgroundColor: 'rgba(102, 126, 234, 0.1)',
  },
  buttonText: {
    fontSize: 14,
    fontWeight: '600',
  },
  chartContainer: {
    alignItems: 'center',
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  candleContainer: {
    height: 220,
    marginVertical: 8,
  },
  candleChart: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    height: 200,
    paddingHorizontal: 10,
  },
  candleWrapper: {
    width: 20,
    marginHorizontal: 2,
    alignItems: 'center',
    justifyContent: 'flex-end',
  },
  wick: {
    width: 2,
  },
  candleBody: {
    width: 12,
  },
  indicators: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: 'rgba(0,0,0,0.1)',
  },
  indicator: {
    alignItems: 'center',
  },
  indicatorLabel: {
    fontSize: 12,
    marginBottom: 4,
  },
  indicatorValue: {
    fontSize: 16,
    fontWeight: 'bold',
  },
});
