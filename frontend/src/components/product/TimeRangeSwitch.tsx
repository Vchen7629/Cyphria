import React from "react"

interface TimeRangeSwitchProps {
    selectedTimeWindow: string
    setSelectedTimeWindow: React.Dispatch<React.SetStateAction<"90d" | "All Time">>
}

/**
 @component

 @description - component for switching between mentions/reviews from the last 90
 days vs all_time. Changes the product rankings based on this
 */
const TimeRangeSwitch = ({ selectedTimeWindow, setSelectedTimeWindow }: TimeRangeSwitchProps) => {

    function handleSetTimeWindowClick(timeWindow: "90d" | "All Time") {
        setSelectedTimeWindow(timeWindow)
    }

    return (
        <div className="flex items-center bg-zinc-800 rounded-lg">
            <button
                onClick={() => handleSetTimeWindowClick("90d")}
                className={`px-2 py-1 text-xs rounded-md border transition-colors ${
                    selectedTimeWindow === "90d"
                        ? "bg-zinc-100 text-zinc-900 border-zinc-100 hover:text-zinc-500"
                        : "text-zinc-400 border-zinc-800 hover:text-zinc-300"
                }`}
            >
                <span>Last 90 Days</span>
            </button>
            <button
                onClick={() => handleSetTimeWindowClick("All Time")}
                className={`px-2 py-1 text-xs rounded-md border transition-colors ${
                    selectedTimeWindow === "All Time"
                        ? "bg-zinc-100 text-zinc-900 border-zinc-100 hover:text-zinc-500"
                        : "text-zinc-400 border-zinc-800 hover:text-zinc-300"
                }`}
            >
                <span>All Time</span>
            </button>
        </div>
    )
}

export default TimeRangeSwitch