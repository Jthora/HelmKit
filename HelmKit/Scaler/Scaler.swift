//
//  Scaler.swift
//  HelmKit
//
//  Created by Jordan Trana on 11/1/18.
//  Copyright © 2018 Jordan Trana. All rights reserved.
//

import Foundation

struct Scaler: Codable {
    
    enum TimeScaleUnit: Int, CaseIterable {
        case custom
        case pt
        case milisec
        case sec
        case min
        case hr
        case day
        case lunar
        case mercury
        case venus
        case earth
        case mars
        case jupiter
        case saturn
        case uranus
        case neptune
        case pluto
        case yuga
        case precession
        
        var name:String {
            switch self {
            case .custom: return "Custom"
            case .pt: return "PlanckTime"
            case .milisec: return "Milisecond"
            case .sec: return "Second"
            case .min: return "Minute"
            case .hr: return "Hour"
            case .day: return "Day"
            case .lunar: return "Lunar"
            case .mercury: return "Mercury"
            case .venus: return "Venus"
            case .earth: return "Earth"
            case .mars: return "Mars"
            case .jupiter: return "Jupiter"
            case .saturn: return "Saturn"
            case .uranus: return "Uranus"
            case .neptune: return "Neptune"
            case .pluto: return "Pluto"
            case .yuga: return "YugaCycle"
            case .precession: return "Precession"
            }
        }
        
        var seconds:TimeInterval {
            switch self {
            case .custom: return 1
            case .pt: return TimeInterval(5.391 * pow(10.0, -44.0))
            case .milisec: return 0.001
            case .sec: return 1
            case .min: return 60
            case .hr: return 3600
            case .day: return 86400
            case .lunar: return 2551392 // (86400 * 29.53)
            case .mercury: return 7600522 // (87.969 * 86400)
            case .venus: return 19414166 // (224.701 * 86400)
            case .earth: return 31557600
            case .mars: return 59354294 // (686.971 * 86400)
            case .jupiter: return 374335776 // (4332.59 * 86400)
            case .saturn: return 929596608 // (10759.22  * 86400)
            case .uranus: return 2651486400 // (30688.5 * 86400)
            case .neptune: return 5199724800 // (60182 * 86400)
            case .pluto: return 7824384000 // (90560 * 86400)
            case .yuga: return 757382400000 // (31557600 * 24000)
            case .precession: return 813302467200 // (31557600 * 25772)
            }
        }
    }
    
    static var defaultScalers: [Scaler] = {
        return [Scaler(name: "Top", unit: .pt, power: 2, scale: 145),
                Scaler(name: "Middle", unit: .sec, power: 10, scale: 1),
                Scaler(name: "Bottom", unit: .day, power: 7, scale: 1)]
    }()
    
    static var multipliers : [String:NSNumber] = { return TranscendentalNumber.dictionary + PrimeNumber.dictionary }()
    
    var unit:TimeScaleUnit
    var power:Double
    var scale:Int
    var name:String
    
    enum CodingKeys: String, CodingKey {
        case unit
        case name
        case power
        case scale
    }
    
    init (name:String, unit:TimeScaleUnit = .pt, power:Double = 2, scale:Int = 150) {
        self.unit = unit
        self.power = power
        self.scale = scale
        self.name = name
    }
    
    init(from decoder: Decoder) throws {
        
        let values = try decoder.container(keyedBy: CodingKeys.self)
        
        let unitInt = try values.decode(Int.self, forKey: .unit)
        if let u = TimeScaleUnit(rawValue: unitInt) {
            unit = u
        } else {
            throw NSError(domain: "TimeScaleUnit not found", code: -1, userInfo: nil)
        }
        name = try values.decode(String.self, forKey: .name)
        power = try values.decode(Double.self, forKey: .power)
        scale = try values.decode(Int.self, forKey: .scale)
    }
    
    func encode(to encoder: Encoder) throws {
        
        var container = encoder.container(keyedBy: CodingKeys.self)
        
        try container.encode(unit.rawValue, forKey: .unit)
        try container.encode(name, forKey: .name)
        try container.encode(power, forKey: .power)
        try container.encode(scale, forKey: .scale)
    }
}
