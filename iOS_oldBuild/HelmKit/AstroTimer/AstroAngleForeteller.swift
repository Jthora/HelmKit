//
//  AstroAngleForeteller.swift
//  HelmKit
//
//  Created by Jordan Trana on 8/1/18.
//  Copyright © 2018 Jordan Trana. All rights reserved.
//

import UIKit
import SwiftAA


// This class is built to Foretell the next (or previous)
// acruaccy within 0.01 seconds

// First version is merely iterative, and just trys to calculate a close-enough

class AstroAngleForeteller {
    
    enum ResonanceType {
        case power // 1/1
        case bonds // 1/2
        case harmony // 1/3
        case change // 1/4
        case style // 1/5
        case ease // 1/6
        case ideals // 1/7
        case strive // 1/8
        case joy // 1/9
        case help // 1/12
        case adjustment // 5/12
        
        func image() -> UIImage? {
            switch self {
            case .power: return UIImage(named: "PowerIcon")
            case .bonds: return UIImage(named: "BondsIcon")
            case .harmony: return UIImage(named: "HarmonyIcon")
            case .change: return UIImage(named: "ChangeIcon")
            case .style: return UIImage(named: "StyleIcon")
            case .ease: return UIImage(named: "EaseIcon")
            case .ideals: return UIImage(named: "IdealsIcon")
            case .strive: return UIImage(named: "StriveIcon")
            case .joy: return UIImage(named: "JoyIcon")
            case .help: return UIImage(named: "HelpIcon")
            case .adjustment: return UIImage(named: "AdjustmentIcon")
            }
        }
        
        func emoji() -> String {
            switch self {
            case .power: return "🤩"
            case .bonds: return "😘"
            case .harmony: return "😁"
            case .change: return "😤"
            case .style: return "😎"
            case .ease: return "☺️"
            case .ideals: return "😇"
            case .strive: return "😠"
            case .joy: return "🥳"
            case .help: return "🤗"
            case .adjustment: return "😒"
            }
        }
            
        func name() -> String {
            switch self {
            case .power: return "Power"
            case .bonds: return "Balance"
            case .harmony: return "Harmony"
            case .change: return "Change"
            case .style: return "Style"
            case .ease: return "Ease"
            case .ideals: return "Ideals"
            case .strive: return "Strive"
            case .joy: return "Joy"
            case .help: return "Help"
            case .adjustment: return "Adjustment"
            }
        }
            
        static func create(from aspect:Astrology.Aspect) -> ResonanceType {
            switch aspect.relation {
            case .conjunction: return .power
            case .opposition: return .bonds
            case .trine: return .harmony
            case .square: return .change
            case .quintile, .biquintile: return .style
            case .sextile: return .ease
            case .septile, .biseptile, .triseptile: return .ideals
            case .semisquare, .bisemisquare: return .strive
            case .novile, .binovile, .trinovile, .quadranovile: return .joy
            case .semisextile: return .help
            case .quincunx: return .adjustment
            }
        }
    }
    
    struct AspectResult {
        
        static let threshold:Double = 1
        static let extreme:Double = 0.001
        
        let aspect:Astrology.Aspect
        var angleSeparation:Degree
        
        var isExtreme:Bool {
            return angleSeparation.value < AspectResult.extreme
        }
        
        var safeAngleSeparation:Degree {
            return Degree(max(abs(angleSeparation.value), AspectResult.extreme))
        }
        
        var powerLevel:Double {
            let orb = aspect.relation.orb.value
            return Double((orb - safeAngleSeparation.value) / orb)
        }
        
        var resonanceScore:Double {
            // Depending on the Planet Combination and type of Aspects, Resonances may go negative
            let planetaryAdjustment = AspectResult.threshold
            let score = (planetaryAdjustment + (1 - planetaryAdjustment) * powerLevel)
            return score
        }
        
        var isSignificant:Bool {
            return resonanceScore > AspectResult.threshold
        }
        
        var resonanceType:ResonanceType {
            return ResonanceType.create(from: aspect)
        }
        
    }
    
    struct AstrologicalReport {
        let date:Date
        let coordinates:[Astrology.AspectBody:EquatorialCoordinates]
        let aspectResults:[AspectResult]
        
        init(date:Date) {
            self.date = date
            let julianDay = JulianDay(date)
            coordinates = [.sun:Sun(julianDay: julianDay).equatorialCoordinates,
            .moon:Moon(julianDay: julianDay).equatorialCoordinates,
            .mercury:Mercury(julianDay: julianDay).equatorialCoordinates,
            .venus:Venus(julianDay: julianDay).equatorialCoordinates,
            .mars:Mars(julianDay: julianDay).equatorialCoordinates,
            .jupiter:Jupiter(julianDay: julianDay).equatorialCoordinates,
            .saturn:Saturn(julianDay: julianDay).equatorialCoordinates,
            .uranus:Uranus(julianDay: julianDay).equatorialCoordinates,
            .neptune:Neptune(julianDay: julianDay).equatorialCoordinates,
            .pluto:Pluto(julianDay: julianDay).apparentGeocentricEquatorialCoordinates]
            aspectResults = AstrologicalReport.createAspectList(from: coordinates)
        }
        
        func coordinate(for aspectBody:Astrology.AspectBody) -> EquatorialCoordinates? {
            return coordinates[aspectBody]
        }
        
        static func createAspectList(from coordinates:[Astrology.AspectBody:EquatorialCoordinates], getAll:Bool = false) -> [AspectResult] {
            
            var aspectList:[AspectResult] = []
            
            for (aspectBody1, equatorialCoordinate1) in coordinates {
                for (aspectBody2, equatorialCoordinate2) in coordinates {
                    let angularSeparation = equatorialCoordinate1.angularSeparation(with: equatorialCoordinate2)
                    let relation = AstroUtils.closestAspectRelation(for: angularSeparation)
                    let aspectResult = AspectResult(aspect: Astrology.Aspect(primarybody: aspectBody1, relation: relation, secondaryBody: aspectBody2), angleSeparation: angularSeparation)
                    if aspectResult.isSignificant || getAll {
                        aspectList.append(aspectResult)
                    }
                }
            }
            return aspectList
        }
    }
    
    struct AstroAngleReport {
        let afterDate:Date
        let aspects:[Date:Astrology.Aspect]
    }
    
    static let DEFAULT_ACCURACY:TimeInterval = (1/1000) // Down to milliseconds of accuracy
    static let DEFAULT_INACCURACY:TimeInterval = 0.5
    
    static func getFullReport(_ afterDate: Date) -> AstroAngleReport {
        
        var aspects:[Date:Astrology.Aspect] = [:]
        
        for primaryBody in Astrology.AspectBody.allCases {
            for relation in Astrology.AspectRelation.allCases {
                for secondaryBody in Astrology.AspectBody.allCases where primaryBody != secondaryBody {
                    let aspect = Astrology.Aspect(primarybody: primaryBody, relation: relation, secondaryBody: secondaryBody)
                    let date = AstroAngleForeteller.whenIsTheDateOfThisNextAspectAlignment(after: afterDate, aspect: aspect)
                    aspects[date] = aspect
                }
            }
        }
        
        return AstroAngleReport(afterDate: afterDate, aspects: aspects)
    }
    
    // This methods does the calculation and returns on a callback... cause this may take a couple iterations: a lot
    static func whenIsTheDateOfThisNextAspectAlignment(after today:Date, aspect:Astrology.Aspect, accuracy:TimeInterval = DEFAULT_ACCURACY) -> Date {
        p1TotalAngleTravel = 0
        startDate = today
        return getDateNextCloser(from: today, aspect: aspect, accuracy: accuracy)
    }
    
    private static var p1LastLong:Degree?
    private static var p2LastLong:Degree?
    private static var p1DegreeBuffer:Degree = 0
    private static var p2DegreeBuffer:Degree = 0
    private static var p1TotalAngleTravel:Degree = 0
    private static var startDate:Date?
    
    private static func getDateNextCloser(from date:Date, aspect:Astrology.Aspect, accuracy:TimeInterval = DEFAULT_ACCURACY, _  i:Int = 0) -> Date {
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
        
        if p1Long + thisAngleDiff > 360 { p1DegreeBuffer += 360 }
        if p2Long + thisAngleDiff > 360 { p2DegreeBuffer += 360 }
        
        if timeUntilArrival < accuracy || i > 500 || p1TotalAngleTravel > 720 {
            if p1TotalAngleTravel > 720 { print("OVER ANGLE: MALFUNCTION") }
            return newDate
        } else {
            return getDateNextCloser(from: newDate, aspect: aspect, i+1)
        }
    }
}
