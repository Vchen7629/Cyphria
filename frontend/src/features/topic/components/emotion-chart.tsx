"use client"

import { PolarAngleAxis, PolarGrid, Radar, RadarChart } from "recharts"

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../shared/ui/shadcn/card"
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "../../../shared/ui/shadcn/chart"
const chartData = [
  { month: "Joy", desktop: 186 },
  { month: "Anger", desktop: 305 },
  { month: "Sadness", desktop: 237 },
  { month: "Surprise", desktop: 273 },
  { month: "Disgust", desktop: 209 },
  { month: "Fear", desktop: 214 },
]

const chartConfig = {
  desktop: {
    label: "Desktop",
    color: "hsl(var(--chart-2))",
  },
} satisfies ChartConfig

export function EmotionsSentimentChart() {
  return (
    <Card className="bg-[#141414] border-2 border-transparent shadow-lg shadow-[hsl(var(--shadow))] w-[23vw] h-[40vh]">
      <CardHeader>
        <CardTitle className="text-2xl font-thin text-gray-400">Emotions Sentiments torwards this topic</CardTitle>
        <CardDescription>
          January - June 2024
        </CardDescription>
      </CardHeader>
      <CardContent className="pb-0">
        <ChartContainer
          config={chartConfig}
          className="mx-auto aspect-square max-h-[250px]"
        >
          <RadarChart data={chartData}>
            <ChartTooltip cursor={false} content={<ChartTooltipContent />} />
            <PolarAngleAxis dataKey="month" />
            <PolarGrid/>
            <Radar
              dataKey="desktop"
              fill="var(--color-desktop)"
              fillOpacity={0.6}
            />
          </RadarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
