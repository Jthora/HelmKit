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
    
    static let DEFAULT_ACCURACY:TimeInterval = (1/1000000) // Down to nanoseconds of accuracy
    
    // This methods does the calculation and returns on a callback... cause this may take a couple iterations: a lot
    static func whenIsTheDateOfThisNextAspectAlignment(after today:Date, aspect:Astrology.Aspect, accuracy:TimeInterval = DEFAULT_ACCURACY, callback:((Date, Int) -> Void)? = nil) {
        DispatchQueue.main.async {
            getDateNextCloser(from: today, aspect: aspect, accuracy: accuracy, callback: callback)
        }
    }
    
    private static func getDateNextCloser(from date:Date, aspect:Astrology.Aspect, accuracy:TimeInterval = DEFAULT_ACCURACY, callback:((Date, Int) -> Void)? = nil, _  i:Int = 0) {
        let diff = aspect.angleDiff(for: date) - aspect.relation.rawValue
        let prototimeUntilArrival1 = TimeInterval((diff.value/360.0))*aspect.primarybody.orbitPeriodInSeconds()
        let newDate = date.addingTimeInterval(prototimeUntilArrival1)
        
        let df = DateFormatter()
        df.dateFormat = "y-MM-dd H:m:ss.SSSS"
        
        print("\(i) : \(diff.value)\nTime until arrival: \(prototimeUntilArrival1)\n\(df.string(from: newDate))")
        if prototimeUntilArrival1 < accuracy || i > 2500 {
            callback?(newDate, i)
        } else {
            getDateNextCloser(from: newDate, aspect: aspect, callback: callback, i+1)
        }
    }
}
