//
//  Astronomy.swift
//  HelmKit
//
//  Created by Jordan Trana on 7/23/18.
//  Copyright © 2018 Jordan Trana. All rights reserved.
//

import Foundation
import UIKit
import SwiftAA

class Astronomy {
    
    enum PlanetsAvailable {
        case mercury
        case venus
        case earth
        case mars
        case jupiter
        case saturn
        case uranus
        case neptune
        case pluto
    }
    
    static func orbitalProgression(_ planet:PlanetsAvailable) -> Degree? {
        switch planet {
        case .mercury: return Planet.mercuryAA.heliocentricEclipticCoordinates.celestialLongitude
        case .venus: return Planet.venusAA.heliocentricEclipticCoordinates.celestialLongitude
        case .earth: return Planet.earthAA.heliocentricEclipticCoordinates.celestialLongitude
        case .mars: return Planet.marsAA.heliocentricEclipticCoordinates.celestialLongitude
        case .jupiter: return Planet.jupiterAA.heliocentricEclipticCoordinates.celestialLongitude
        case .saturn: return Planet.saturnAA.heliocentricEclipticCoordinates.celestialLongitude
        case .uranus: return Planet.uranusAA.heliocentricEclipticCoordinates.celestialLongitude
        case .neptune: return Planet.neptuneAA.heliocentricEclipticCoordinates.celestialLongitude
        case .pluto: return Planet.plutoAA.position().celestialLongitude
        }
    }
    
    static func moonPhaseAngle() -> Degree {
        return Planet.moonAA.phaseAngle()
    }
}

extension Planet: Hashable {
    var hashValue: Int {
        return name.hash
    }
}

extension SwiftAA.Planet {
    func position() -> (EclipticCoordinates) {
        return self.heliocentricEclipticCoordinates
    }
}

extension SwiftAA.Earth {
    func position() -> (EclipticCoordinates) {
        return self.heliocentricEclipticCoordinates
    }
}

extension SwiftAA.Pluto {
    func position() -> (EclipticCoordinates) {
        return EclipticCoordinates(lambda: Degree(self.ellipticalObjectDetails.HeliocentricEclipticLongitude),
                                   beta: Degree(self.ellipticalObjectDetails.HeliocentricEclipticLatitude))
    }
}

extension SwiftAA.PlanetaryBase {
    func position() -> (EclipticCoordinates) {
        let longitude = KPCAAEclipticalElement_EclipticLongitude(self.julianDay.value, self.planet, self.highPrecision)
        let latitude = KPCAAEclipticalElement_EclipticLatitude(self.julianDay.value, self.planet, self.highPrecision)
        return EclipticCoordinates(lambda: Degree(longitude), beta: Degree(latitude))
    }
}

struct Planet: Equatable {
    
    let type: Astronomy.PlanetsAvailable?
    
    static func ==(lhs: Planet, rhs: Planet) -> Bool {
        return lhs.name == rhs.name &&
            lhs.orbitalRadius == rhs.orbitalRadius &&
            lhs.displayOrbitalRadius == rhs.displayOrbitalRadius &&
            lhs.radius == rhs.radius &&
            lhs.rotationDuration == rhs.rotationDuration &&
            lhs.axialTilt == rhs.axialTilt &&
            lhs.orbitPeriod == rhs.orbitPeriod
    }
    
    let name: String
    
    // Distance from the sun in millions of km
    // Source: http://www.enchantedlearning.com/subjects/astronomy/planets/
    var orbitalRadius: CGFloat
    
    var displayOrbitalRadius: CGFloat {
        get {
            return orbitalRadius / 100
        }
    }
    
    // In KM: eg. Earth 6371.0
    // Source: https://en.wikipedia.org/wiki/List_of_Solar_System_objects_by_size
    let radius: Float
    
    // In HOURS 🕥: eg. Earth 23.93, Mercury 1407.6
    // Source: https://en.m.wikipedia.org/wiki/Axial_tilt#Solar_System_bodies
    let rotationDuration: Double
    
    // Tilt on the poles in degrees: eg. Earth 23.44
    // Source: https://en.m.wikipedia.org/wiki/Axial_tilt#Solar_System_bodies
    let axialTilt: Float
    
    // Duration to circle the sun in earth YEARS 📅
    // Source: https://en.wikipedia.org/wiki/Orbital_period#Examples_of_sidereal_and_synodic_periods
    let orbitPeriod: Double
    var orbitPeriodInSeconds: TimeInterval {
        return orbitPeriod * 31557600
    }
    
    
    static var timeOffset:TimeInterval?
    static var customDate:Date?
    static var date:Date {
        guard customDate != nil else { return timeOffset != nil ? Date().addingTimeInterval(timeOffset!) : Date() }
        return timeOffset != nil ? customDate!.addingTimeInterval(timeOffset!) : customDate!
    }
    
    static var julianDay:JulianDay {
        return JulianDay(date)
    }
    
    static var mercuryAA:Mercury { return Mercury(julianDay: julianDay) }
    static var venusAA:Venus { return Venus(julianDay: julianDay) }
    static var earthAA:Earth { return Earth(julianDay: julianDay) }
    static var marsAA:Mars { return Mars(julianDay: julianDay) }
    static var jupiterAA:Jupiter { return Jupiter(julianDay: julianDay) }
    static var saturnAA:Saturn { return Saturn(julianDay: julianDay) }
    static var uranusAA:Uranus { return Uranus(julianDay: julianDay) }
    static var neptuneAA:Neptune { return Neptune(julianDay: julianDay) }
    static var plutoAA:Pluto { return Pluto(julianDay: julianDay) }
    static var moonAA:Moon { return Moon(julianDay: julianDay) }
    
    static let sun = Planet(type: nil, name: "Sun", orbitalRadius: 0, radius: 695700, rotationDuration: 1000, axialTilt: 1, orbitPeriod: 1)
    static let mercury = Planet(type: .mercury, name: mercuryAA.name, orbitalRadius: 57.9, radius: 2439.7, rotationDuration: 1407.6, axialTilt: 0.03, orbitPeriod: 0.24084204)
    static let venus = Planet(type: .venus, name: venusAA.name, orbitalRadius: 108.2, radius: 6051.8, rotationDuration: 5832.6, axialTilt: 2.64, orbitPeriod: 0.61517237)
    static let mars = Planet(type: .mars, name: marsAA.name, orbitalRadius: 227.9, radius: 3389.5, rotationDuration: 24.62, axialTilt: 25.19, orbitPeriod: 1.8808524)
    static let jupiter = Planet(type: .jupiter, name: jupiterAA.name, orbitalRadius: 778.3, radius: 69911, rotationDuration: 9.93, axialTilt: 3.13, orbitPeriod: 11.86631421)
    static let saturn = Planet(type: .saturn, name: saturnAA.name, orbitalRadius: 1427, radius: 58232, rotationDuration: 10.66, axialTilt: 26.73, orbitPeriod: 29.47305083)
    static let uranus = Planet(type: .uranus, name: uranusAA.name, orbitalRadius: 2871, radius: 25362, rotationDuration: 17.24, axialTilt: 82.23, orbitPeriod: 84.05122725)
    static let neptune = Planet(type: .neptune, name: neptuneAA.name, orbitalRadius: 4497, radius: 24622, rotationDuration: 16.11, axialTilt: 28.32, orbitPeriod: 164.88839750)
    static let pluto = Planet(type: .pluto, name: plutoAA.name, orbitalRadius: 5907, radius: 1188, rotationDuration: 153.288, axialTilt: 122.53, orbitPeriod: 248.12989786)
    
    static let allPlanets = [sun, mercury, venus, mars, jupiter, saturn, uranus, neptune, pluto]
    
    static func planet(_ planet:Astronomy.PlanetsAvailable) -> Planet {
        return allPlanets.first(where: { $0.type == planet })!
    }
}
