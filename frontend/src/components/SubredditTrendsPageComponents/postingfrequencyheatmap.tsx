import { useState } from 'react';

export function PostingFrequencyHeatMapChart() {
    const generateData = (count: any, { min, max }: { min: number, max: number}) => {
        return Array.from({ length: count }, () => 
          Math.floor(Math.random() * (max - min + 1)) + min
        );
      };
    
      const days = ['monday', 'tuesday', 'wednsday', 'thursday', 'friday', 'saturday', 'sunday'];
      const hours = [
        '12am', '1am', '2am', '3am', '4am', '5am', '6am', '7am', '8am', '9am', '10am', '11am', 
        '12pm', '1pm', '2pm', '3pm', '4pm', '5pm', '6pm', '7pm', '8pm', '9pm', '10pm', '11pm'
      ]
      const [hoveredCell, setHoveredCell] = useState<any>(null);
    
      const data = days.map(days => ({
        name: days,
        values: generateData(24, { min: -30, max: 55 })
      }));
    
      const getColor = (value: number) => {
        if (value <= 5) return '#005F7F';
        if (value <= 20) return '#00E5FF';
        if (value <= 45) return '#BF40BF';
        return '#daa520';
      };
    
      const cellWidth = 70;
      const cellHeight = 34;
    
      return (
        <div className="flex flex-col items-center bg-[#141414] border-2 border-bordercolor w-[25vw] h-[74vh] py-[2vh] rounded-2xl">
          <h2 className="text-3xl font-thin text-gray-400 mb-[2vh]">HeatMap Chart For Posting Frequency</h2>
          
          <div className="relative">
            <div className="flex ">
              <div className="w-20" />
              {days.map((day, i) => (
                <div 
                  key={i}
                  className="font-medium flex justify-center"
                  style={{ width: cellWidth }}
                >
                  {day}
                </div>
              ))}
            </div>

            <div className="flex">
              <div className="w-20">
                {hours.map((hour, i) => (
                  <div
                    key={i}
                    className="text-gray-400 flex items-center"
                    style={{ height: cellHeight }}
                  >
                    {hour}
                  </div>
                ))}
            </div>

          <div className="flex">
            {days.map((day, dayIndex) => (
              <div key={day} className="flex flex-col">
                {hours.map((hour, hourIndex) => (
                  <div
                    key={`${dayIndex}-${hourIndex}`}
                    style={{
                      width: cellWidth,
                      height: cellHeight,
                      backgroundColor: getColor(data[dayIndex].values[hourIndex]),
                      transition: 'all 0.2s',
                      opacity: hoveredCell === `${dayIndex}-${hourIndex}` ? 0.8 : 1
                    }}
                    className="border border-white/10 cursor-pointer"
                    onMouseEnter={() => setHoveredCell(`${dayIndex}-${hourIndex}`)}
                    onMouseLeave={() => setHoveredCell(null)}
                  >
                    {hoveredCell === `${dayIndex}-${hourIndex}` && (
                      <div className="absolute z-30 bg-gray-800 p-2 rounded shadow-lg text-sm text-white">
                        <div className="font-bold capitalize">{day}</div>
                        <div>{hour}</div>
                        <div>Value: {data[dayIndex].values[hourIndex]}</div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="flex gap-4 justify-center mt-4">
        {[
          { range: "Low (-30 to 5)", color: "#005F7F" },
          { range: "Medium (6 to 20)", color: "#00E5FF" },
          { range: "High (21 to 45)", color: "#BF40BF" },
          { range: "Extreme (46 to 55)", color: "#daa520" }
        ].map((item, index) => (
          <div key={index} className="flex items-center gap-2">
            <div 
              className="w-3 h-3" 
              style={{ backgroundColor: item.color }}
            />
            <span className="text-sm text-gray-400">{item.range}</span>
          </div>
        ))}
      </div>
    </div>
  );
};