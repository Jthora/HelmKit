//
//  AstroUtils.swift
//  HelmKit
//
//  Created by Jordan Trana on 7/28/18.
//  Copyright © 2018 Jordan Trana. All rights reserved.
//

import Foundation
import SwiftAA


struct AstroUtils {
    
    
    /// Get Closest Date for Aspect realtive to Date
    
    static let allAspectRelationTypes:[Astrology.AspectRelation] = [.conjunction,
                                                                    .semisextile,
                                                                    .novile,
                                                                    .semisquare,
                                                                    .sextile,
                                                                    .quintile,
                                                                    .square,
                                                                    .trine,
                                                                    .biquintile,
                                                                    .quincunx,
                                                                    .opposition]
    
    static func getAllAspects(within timeRange:TimeInterval = 3600) {
        
        // Sun - Earth - Moon
        
        // Earth - Moon - Planet
        
        // Sun - Earth - Planet
        
        // Sun - Planet - Planet
    }
    
    // if returns nil that means none within timeRange
    static func getClosestAspectForMoon(closeTo date:Date) -> AstroAspectTimeReport? {
        
        let moonCurrentAngle = Astronomy.moonPhaseAngle()
        let (relation, degreeDiff) = closestAspectRelationForAngle(angle: moonCurrentAngle)
        
        guard relation.orb > abs(degreeDiff) else { return nil }
        
        let aspect = Astrology.Aspect(primarybody: .moon, relation: relation, secondaryBody: .sun)
        return AstroAspectTimeReport(date: date, aspect: aspect)
    }
    
    static func planet(_ planet:Astronomy.PlanetsAvailable) -> SwiftAA.EllipticalPlanetaryDetails? {
        switch planet {
        case .mercury: return Planet.mercuryAA
        case .venus: return Planet.venusAA
        case .earth: return nil
        case .mars: return Planet.marsAA
        case .jupiter: return Planet.jupiterAA
        case .saturn: return Planet.saturnAA
        case .uranus: return Planet.uranusAA
        case .neptune: return Planet.neptuneAA
        case .pluto: return Planet.plutoAA
        }
    }
    
    static func closestAspectRelationForAngle(angle:Degree) -> (Astrology.AspectRelation, Degree) {
        var closestAspectRelation:Astrology.AspectRelation = .opposition
        var degreeDiff:Degree = 360
        
        for aspect in allAspectRelationTypes {
            let thisDegreeDiff:Degree = abs(aspect.rawValue - angle)
            if degreeDiff > thisDegreeDiff {
                closestAspectRelation = aspect
                degreeDiff = thisDegreeDiff
            }
        }
        
        
        return (closestAspectRelation, degreeDiff)
    }
    
    static func getClosestAspect(between firstPlanet:Astrology.AspectBody, and secondPlanet:Astrology.AspectBody) -> AstroAspectTimeReport? {
        
        let primaryPhaseAngle = planet(firstPlanet.toAstronomy()!)!.phaseAngle
        let secondaryPhaseAngle = planet(secondPlanet.toAstronomy()!)!.phaseAngle
        let (relation, degreeDiff) = closestAspectRelationForAngle(angle: primaryPhaseAngle - secondaryPhaseAngle)
        
        guard relation.orb > abs(degreeDiff) else { return nil }
        
        let orbitPeriod = Planet.planet(firstPlanet.toAstronomy()!).orbitPeriodInSeconds
        let secondsUntil:TimeInterval = TimeInterval(degreeDiff.value/360.0)*orbitPeriod
        let date = Date(timeIntervalSinceNow: secondsUntil)
        let aspect = Astrology.Aspect(primarybody: firstPlanet, relation: relation, secondaryBody: secondPlanet)
        return AstroAspectTimeReport(date: date, aspect: aspect)
    }
}

struct AstroAspectTimeReport {
    
    /// Date and Time the Aspect is to occur
    var date:Date
    
    /// The Aspect itself
    var aspect:Astrology.Aspect
    
    /// Convenience
    var primaryBody:Astrology.AspectBody { return aspect.primarybody }
    var secondaryBody:Astrology.AspectBody { return aspect.secondaryBody }
    var relation:Astrology.AspectRelation { return aspect.relation }
    
    /// Calculations for Primary Body Distance
    var primaryBodyDistance:Meter { return 0 }
    var primaryBodyAngleRemaining:Degree { return 0 }
    
    /// Calculations for Secondary Body Distance
    var secondBodyDistance:Meter { return 0 }
    var secondBodyAngleRemaining:Degree { return 0 }
    
    /// Calculations for remainin
    var timeOffset:TimeInterval { return date.timeIntervalSince(Date()) }
}




extension Astronomy.PlanetsAvailable {
    func toAstrology() -> Astrology.AspectBody? {
        switch self {
        case .mercury: return .mercury
        case .venus: return .venus
        case .mars: return .mars
        case .jupiter: return .jupiter
        case .saturn: return .saturn
        case .uranus: return .uranus
        case .neptune: return .neptune
        case .pluto: return .pluto
        default: return nil
        }
    }
}

extension Astrology.AspectBody {
    func toAstronomy() -> Astronomy.PlanetsAvailable? {
        switch self {
        case .mercury: return .mercury
        case .venus: return .venus
        case .mars: return .mars
        case .jupiter: return .jupiter
        case .saturn: return .saturn
        case .uranus: return .uranus
        case .neptune: return .neptune
        case .pluto: return .pluto
        default: return nil
        }
    }
}
