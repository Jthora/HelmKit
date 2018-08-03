//
//  AstroAngleForeteller.swift
//  HelmKit
//
//  Created by Jordan Trana on 8/1/18.
//  Copyright © 2018 Jordan Trana. All rights reserved.
//

import Foundation
import SwiftAA


// This class is built to Foretell the next (or previous)
// acruaccy within 0.01 seconds

// First version is merely iterative, and just trys to calculate a close-enough

class AstroAngleForeteller {
    
    static let DEFAULT_ACCURACY:TimeInterval = (1/1000) // Down to milliseconds of accuracy
    static let DEFAULT_INACCURACY:TimeInterval = 0.5
    
    // This methods does the calculation and returns on a callback... cause this may take a couple iterations: a lot
    static func whenIsTheDateOfThisNextAspectAlignment(after today:Date, aspect:Astrology.Aspect, accuracy:TimeInterval = DEFAULT_ACCURACY, callback:((Date, Int) -> Void)? = nil) {
        p1TotalAngleTravel = 0
        startDate = today
        getDateNextCloser(from: today, aspect: aspect, accuracy: accuracy, callback: callback)
    }
    
    private static var p1LastLong:Degree?
    private static var p2LastLong:Degree?
    private static var p1DegreeBuffer:Degree = 0
    private static var p2DegreeBuffer:Degree = 0
    private static var p1TotalAngleTravel:Degree = 0
    private static var startDate:Date?
    
    private static func getDateNextCloser(from date:Date, aspect:Astrology.Aspect, accuracy:TimeInterval = DEFAULT_ACCURACY, callback:((Date, Int) -> Void)? = nil, _  i:Int = 0) {
        let p1Long = aspect.primarybody.celestialLongitude(date)!
        let p2Long = aspect.secondaryBody.celestialLongitude(date)!
        
        //((p1Long + p1DegreeBuffer) - (p2Long + p2DegreeBuffer))
        let thisAngleDiff:Degree = abs(abs(p1Long - p2Long) - aspect.relation.rawValue)
        
        p1LastLong = p1Long
        p2LastLong = p2Long
        
        p1TotalAngleTravel += abs(thisAngleDiff)
        
        //if thisAngleDiff < 0 { thisAngleDiff += 360 }
        
        let timeUntilArrival = abs(TimeInterval((thisAngleDiff.value/360.0))*(aspect.primarybody.orbitPeriodInSeconds() * DEFAULT_INACCURACY))
        let newDate = date.addingTimeInterval(timeUntilArrival)
        
        let df = DateFormatter()
        df.dateFormat = "y-MM-dd H:m:ss.SSSS"
        print("\(i) : \(thisAngleDiff.value)\n\(p1Long) - \(p2Long)")
        print("\((p1Long + p1DegreeBuffer)) - \((p2Long + p2DegreeBuffer)))\nNext sample:\n\(timeUntilArrival) seconds offset\n\(df.string(from: newDate))\n")
        
        if p1Long + thisAngleDiff > 360 { p1DegreeBuffer += 360 }
        if p2Long + thisAngleDiff > 360 { p2DegreeBuffer += 360 }
        
        if timeUntilArrival < accuracy || i > 500 || p1TotalAngleTravel > 720 {
            if p1TotalAngleTravel > 720 { print("OVER ANGLE: MALFUNCTION") }
            callback?(newDate, i)
            print("Total Angle Travel: \(p1TotalAngleTravel)\nTotal Years Until: \(newDate.timeIntervalSince(startDate!).toYears())")
        } else {
            getDateNextCloser(from: newDate, aspect: aspect, callback: callback, i+1)
        }
    }
}
