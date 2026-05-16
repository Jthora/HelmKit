//
//  AstroMath.swift
//  HelmKit
//
//  Created by Jordan Trana on 7/28/18.
//  Copyright © 2018 Jordan Trana. All rights reserved.
//

import Foundation
import SwiftAA

// Calculate date and time until conjunction and opposition between the moon a planet and earth

// Calculate date and time until conjunction and opposition in either past or future between a planet and earth

// Calculate date and time until/since conjunction and opposition in either past or future between a planet and another planet (that is not earth) [this method may be used for the earth-specific calculation]

// Calculate StarPulse
// Calculating StarPulse is the reason I'm doing this project.
// SO I can demonstrate, using real astrologically visualized astronomical calculations, When and how the StarPulse proceeds
// #cosmicawareness101



typealias Hz = Double
extension Hz {
    func toTimeInterval() -> TimeInterval {
        return self == 0 ? 0 : 1.0/self
    }
}
extension TimeInterval {
    
    func toHz() -> Hz {
        return self/1.0
    }
}
