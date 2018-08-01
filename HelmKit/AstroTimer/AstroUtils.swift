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
    
    static let astrologyPlanets:[Astrology.AspectBody] = [.mercury,
                                                     .venus,
                                                     .mars,
                                                     .jupiter,
                                                     .saturn,
                                                     .uranus,
                                                     .neptune,
                                                     .pluto]
    
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
    
    static func getAllAspects(closeTo date:Date = Date()) {
        
        // Sun - Earth - Moon
        let nextMoonAspect = getClosestAspectForMoon(closeTo: date)
        
        // Earth - Moon - Planet
        
        
        // Sun - Earth - Planet
        
        // Sun - Planet - Planet
    }
    
    static func getNextAspectsBetweenMoonAndPlanets(useOrbRange:Bool = true) -> [AstroAspectTimeReport] {
        var reports:[AstroAspectTimeReport] = []
        
        for planet in astrologyPlanets {
            if let report = getClosestAspectForMoon(with: planet) {
                guard !useOrbRange || report.withinRange else {  continue }
                reports.append(report)
            }
        }
        
        return reports
    }
    
    // if returns nil that means none within timeRange
    static func getClosestAspectForMoon(closeTo date:Date) -> AstroAspectTimeReport? {
        
        let moonCurrentAngle = Astronomy.moonPhaseAngle()
        let (relation, degreeDiff) = closestAspectRelationForAngle(angle: moonCurrentAngle)
        
        let aspect = Astrology.Aspect(primarybody: .moon, relation: relation, secondaryBody: .sun)
        return AstroAspectTimeReport(date: date, aspect: aspect, distance: degreeDiff)
    }
    
    static func getClosestAspectForMoon(with planet:Astrology.AspectBody) -> AstroAspectTimeReport? {
        
        let moonPhaseAngle = Astronomy.moonPhaseAngle()
        let planetPhaseAngle = planet.geocentricLongitude()!
        let (relation, degreeDiff) = closestAspectRelationForAngle(angle: moonPhaseAngle - planetPhaseAngle)
        
        let orbitPeriod = planet.orbitPeriodInSeconds()
        let secondsUntil:TimeInterval = TimeInterval(degreeDiff.value/360.0)*orbitPeriod
        let date = Date(timeIntervalSinceNow: secondsUntil)
        
        let aspect = Astrology.Aspect(primarybody: .moon, relation: relation, secondaryBody: .sun)
        return AstroAspectTimeReport(date: date, aspect: aspect, distance: degreeDiff)
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
        
        let primaryAngle = firstPlanet.heliocentricPosition()
        let secondaryAngle = firstPlanet.heliocentricPosition()
        let (relation, degreeDiff) = closestAspectRelationForAngle(angle: primaryAngle - secondaryAngle)
        
        guard relation.orb > abs(degreeDiff) else { return nil }
        
        let orbitPeriod = firstPlanet.orbitPeriodInSeconds()
        let secondsUntil:TimeInterval = TimeInterval(degreeDiff.value/360.0)*orbitPeriod
        let date = Date(timeIntervalSinceNow: secondsUntil)
        
        let aspect = Astrology.Aspect(primarybody: firstPlanet, relation: relation, secondaryBody: secondPlanet)
        return AstroAspectTimeReport(date: date, aspect: aspect, distance: degreeDiff)
    }
}

struct AstroAspectTimeReport {
    
    /// Date and Time the Aspect is to occur
    var date:Date
    
    /// The Aspect itself
    var aspect:Astrology.Aspect
    
    /// Angle Distance
    var distance:Degree
    
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
    
    /// Is this aspect within Orb Range
    var withinRange:Bool { return relation.orb > abs(distance) }
}




extension Astronomy.PlanetsAvailable {
    func toAstrology() -> Astrology.AspectBody? {
        switch self {
        case .earth: return .sun
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
    
    func toPlanet() -> Planet? {
        switch self {
        case .mercury: return Planet.mercury
        case .venus: return Planet.venus
        case .mars: return Planet.mars
        case .jupiter: return Planet.jupiter
        case .saturn: return Planet.saturn
        case .uranus: return Planet.uranus
        case .neptune: return Planet.neptune
        case .pluto: return Planet.pluto
        default: return nil
        }
    }
}

extension Astrology.AspectBody {
    
    func celestialLongitude(_ date:Date? = nil) -> Degree? {
        if let date = date {
            switch self {
            case .sun: return Planet.earthAA(date).position().celestialLongitude
            case .mercury: return Planet.mercuryAA(date).position().celestialLongitude
            case .venus: return Planet.venusAA(date).position().celestialLongitude
            case .mars: return Planet.marsAA(date).position().celestialLongitude
            case .jupiter: return Planet.jupiterAA(date).position().celestialLongitude
            case .saturn: return Planet.saturnAA(date).position().celestialLongitude
            case .uranus: return Planet.uranusAA(date).position().celestialLongitude
            case .neptune: return Planet.neptuneAA(date).position().celestialLongitude
            case .pluto: return Planet.plutoAA(date).position().celestialLongitude
            default: return nil
            }
        }
        switch self {
        case .sun: return Planet.earthAA.position().celestialLongitude
        case .mercury: return Planet.mercuryAA.position().celestialLongitude
        case .venus: return Planet.venusAA.position().celestialLongitude
        case .mars: return Planet.marsAA.position().celestialLongitude
        case .jupiter: return Planet.jupiterAA.position().celestialLongitude
        case .saturn: return Planet.saturnAA.position().celestialLongitude
        case .uranus: return Planet.uranusAA.position().celestialLongitude
        case .neptune: return Planet.neptuneAA.position().celestialLongitude
        case .pluto: return Planet.plutoAA.position().celestialLongitude
        default: return nil
        }
    }
    
    func geocentricLongitude(_ date:Date? = nil) -> Degree? {
        if let date = date {
            switch self {
            case .moon: return Planet.moonAA(date).apparentEquatorialCoordinates.declination
            case .mercury: return Planet.mercuryAA(date).apparentGeocentricEquatorialCoordinates.declination
            case .venus: return Planet.venusAA(date).apparentGeocentricEquatorialCoordinates.declination
            case .mars: return Planet.marsAA(date).apparentGeocentricEquatorialCoordinates.declination
            case .jupiter: return Planet.jupiterAA(date).apparentGeocentricEquatorialCoordinates.declination
            case .saturn: return Planet.saturnAA(date).apparentGeocentricEquatorialCoordinates.declination
            case .uranus: return Planet.uranusAA(date).apparentGeocentricEquatorialCoordinates.declination
            case .neptune: return Planet.neptuneAA(date).apparentGeocentricEquatorialCoordinates.declination
            case .pluto: return Planet.plutoAA(date).apparentGeocentricEquatorialCoordinates.declination
            default: return nil
            }
        }
        switch self {
        case .mercury: return Planet.mercuryAA.apparentGeocentricEquatorialCoordinates.declination
        case .venus: return Planet.venusAA.apparentGeocentricEquatorialCoordinates.declination
        case .mars: return Planet.marsAA.apparentGeocentricEquatorialCoordinates.declination
        case .jupiter: return Planet.jupiterAA.apparentGeocentricEquatorialCoordinates.declination
        case .saturn: return Planet.saturnAA.apparentGeocentricEquatorialCoordinates.declination
        case .uranus: return Planet.uranusAA.apparentGeocentricEquatorialCoordinates.declination
        case .neptune: return Planet.neptuneAA.apparentGeocentricEquatorialCoordinates.declination
        case .pluto: return Planet.plutoAA.apparentGeocentricEquatorialCoordinates.declination
        default: return nil
        }
    }
    
    func toAstronomy() -> Astronomy.PlanetsAvailable? {
        switch self {
        case .sun: return .earth
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
    
    func orbitPeriodInSeconds() -> TimeInterval {
        return Planet.planet(self.toAstronomy()!).orbitPeriodInSeconds
    }
    
    func heliocentricPosition() -> Degree {
        return Planet.planet(self.toAstronomy()!).heliocentricPosition!
    }
}
