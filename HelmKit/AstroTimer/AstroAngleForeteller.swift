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
    
    // This methods does the calculation and returns on a callback... cause this may take a couple iterations: a lot
    static func whenIsTheDateOfThisNextAspectAlignment(after today:Date, aspect:Astrology.Aspect, accuracy:TimeInterval = 0.01, callback:((Date, Int) -> Void)? = nil) {
        DispatchQueue.main.async {
            getDateNextCloser(from: today, aspect: aspect, accuracy: accuracy, callback: callback)
        }
    }
    
    private static func getDateNextCloser(from date:Date, aspect:Astrology.Aspect, accuracy:TimeInterval = 0.01, callback:((Date, Int) -> Void)? = nil, _  i:Int = 0) {
        let diff = aspect.angleDiff(for: date) - aspect.relation.rawValue
        
        let prototimeUntilArrival1 = TimeInterval((diff.value/360.0))*aspect.primarybody.orbitPeriodInSeconds()
        let prototimeUntilArrival2 = TimeInterval((diff.value/360.0))*aspect.secondaryBody.orbitPeriodInSeconds()
        
        let avg = (prototimeUntilArrival1 + prototimeUntilArrival2) / 2
        let newDate = date.addingTimeInterval(avg)
        print("\(i) : \(diff.value) : \(avg)\nprototimeUntilArrival1: \(prototimeUntilArrival1)\nprototimeUntilArrival2: \(prototimeUntilArrival2)\n\(date)\n")
        if avg < accuracy || i > 10000 {
            callback?(newDate, i)
        } else {
            getDateNextCloser(from: newDate, aspect: aspect, callback: callback, i+1)
        }
    }
}
