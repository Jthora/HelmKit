//
//  Ticker.swift
//  HelmKit
//
//  Created by Jordan Trana on 11/4/18.
//  Copyright © 2018 Jordan Trana. All rights reserved.
//

import UIKit

struct Tick {
    var date:Date
    var i:Int
    var offset:Double
}

class Ticker: NSObject, AstroTimerDelegate {
    
    var scalers:[Scaler] {
        return App.state.scalers
    }
    
    override init() {
        super.init()
        setup()
    }
    
    func setup() {
        AstroTimer.addDelegate(delegate: self, priority: .first)
    }
    
    func start() {
        AstroTimer.start()
    }
    
    func didUpdate(_ astroTimer: AstroTimer, _ timePoint: AstroTimePoint) {
        guard let timeVector = astroTimer.timeVector else { return }
        for scaler in scalers {
            let ticks = getTicks(timeVector: timeVector, timePoint: timePoint, scaler: scaler)
            // For each ticker, get the ticks and pass them along to a delegate for this ticker
            // that way we can position the sprites relative to the points on the screen via the X position on-screen
            
            
        }
    }
    
    func getTicks(timeVector:AstroTimeVector, timePoint:AstroTimePoint, scaler:Scaler) -> [Tick] {
        let centralDate:Date = timePoint.date
        let totalTicks:Double = Double(scaler.tickCount)
        let timeWindow:TimeInterval = scaler.timeWindow
        let timeWindowRange:TimeInterval = timeWindow/2.0
        let halfBeforeDate:Date = centralDate.addingTimeInterval(-timeWindowRange)
        
        // Calculate the number of Ticks visible in this TimeWindow
        let planetDegreeOffset = timePoint.degrees(for: scaler.planetFocus)
        let degreeToTimeIntervalRatio = timeVector.degrees(for: scaler.planetFocus).value
        let tickToDegreeRatio = totalTicks / 360.0
        let tickToTimeIntervalRatio = tickToDegreeRatio * degreeToTimeIntervalRatio
        let vectorToTimeWindowRatio = timeWindow / timeVector.scale
        let ticksPerTimeWindow = tickToTimeIntervalRatio * vectorToTimeWindowRatio
        
        let planetTickOffset = planetDegreeOffset.value * tickToDegreeRatio
        
        // For number of Degrees range and seconds window, how many ticks?
        var ticks:[Tick] = []
        
        for i in 0...Int(ticksPerTimeWindow) {
            let tickDate = Date(timeInterval: 0, since: halfBeforeDate)
            let offset = (planetTickOffset + (Double(i) * tickToTimeIntervalRatio))/timeWindow
            let tick = Tick(date: tickDate, i: i, offset: offset)
            ticks.append(tick)
        }
        return ticks
    }
}
