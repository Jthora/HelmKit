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
    
    static func orbitalProgression(_ planet:SwiftAA.PlanetaryOrbits) -> Degree? {
        switch planet {
        case is Mercury: return Planet.mercuryAA.heliocentricEclipticCoordinates.celestialLongitude
        case is Venus: return Planet.venusAA.heliocentricEclipticCoordinates.celestialLongitude
        case is Earth: return Planet.earthAA.heliocentricEclipticCoordinates.celestialLongitude
        case is Mars: return Planet.marsAA.heliocentricEclipticCoordinates.celestialLongitude
        case is Jupiter: return Planet.jupiterAA.heliocentricEclipticCoordinates.celestialLongitude
        case is Saturn: return Planet.saturnAA.heliocentricEclipticCoordinates.celestialLongitude
        case is Uranus: return Planet.uranusAA.heliocentricEclipticCoordinates.celestialLongitude
        case is Neptune: return Planet.neptuneAA.heliocentricEclipticCoordinates.celestialLongitude
        default: return nil
        }
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
    
    let type: SwiftAA.Planet.Type?
    
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
    
    static var mercuryAA:Mercury { return Mercury(julianDay: JulianDay(Date())) }
    static var venusAA:Venus { return Venus(julianDay: JulianDay(Date())) }
    static var earthAA:Earth { return Earth(julianDay: JulianDay(Date())) }
    static var marsAA:Mars { return Mars(julianDay: JulianDay(Date())) }
    static var jupiterAA:Jupiter { return Jupiter(julianDay: JulianDay(Date())) }
    static var saturnAA:Saturn { return Saturn(julianDay: JulianDay(Date())) }
    static var neptuneAA:Neptune { return Neptune(julianDay: JulianDay(Date())) }
    static var uranusAA:Uranus { return Uranus(julianDay: JulianDay(Date())) }
    static var plutoAA:Pluto { return Pluto(julianDay: JulianDay(Date())) }
    
    static let sun = Planet(type: nil, name: "Sun", orbitalRadius: 0, radius: 695700, rotationDuration: 1000, axialTilt: 1, orbitPeriod: 1)
    static let mercury = Planet(type: Mercury.self, name: mercuryAA.name, orbitalRadius: 57.9, radius: 2439.7, rotationDuration: 1407.6, axialTilt: 0.03, orbitPeriod: 0.240846)
    static let venus = Planet(type: Venus.self, name: venusAA.name, orbitalRadius: 108.2, radius: 6051.8, rotationDuration: 5832.6, axialTilt: 2.64, orbitPeriod: 0.615)
    static let mars = Planet(type: Mars.self, name: marsAA.name, orbitalRadius: 227.9, radius: 3389.5, rotationDuration: 24.62, axialTilt: 25.19, orbitPeriod: 1.881)
    static let jupiter = Planet(type: Jupiter.self, name: jupiterAA.name, orbitalRadius: 778.3, radius: 69911, rotationDuration: 9.93, axialTilt: 3.13, orbitPeriod: 11.86)
    static let saturn = Planet(type: Saturn.self, name: saturnAA.name, orbitalRadius: 1427, radius: 58232, rotationDuration: 10.66, axialTilt: 26.73, orbitPeriod: 29.46)
    static let uranus = Planet(type: Uranus.self, name: uranusAA.name, orbitalRadius: 2871, radius: 25362, rotationDuration: 17.24, axialTilt: 82.23, orbitPeriod: 84.01)
    static let neptune = Planet(type: Neptune.self, name: neptuneAA.name, orbitalRadius: 4497, radius: 24622, rotationDuration: 16.11, axialTilt: 28.32, orbitPeriod: 164.8)
    
    static let allPlanets = [sun, mercury, venus, mars, jupiter, saturn, uranus, neptune]
}
