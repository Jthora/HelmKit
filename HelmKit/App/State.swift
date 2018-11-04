//
//  ScalarState.swift
//  HelmKit
//
//  Created by Jordan Trana on 11/1/18.
//  Copyright © 2018 Jordan Trana. All rights reserved.
//

import Foundation

class State {
    
    private let KEY_SCALARS = "KEY_SCALARS"
    private let KEY_CURRENTSCALAR = "KEY_CURRENTSCALAR"
    
    var scalers:[Scaler] = Scaler.defaultScalers
    var selectedScalerIndex:Int = 0
    var currentScaler:Scaler {
        get {
            return scalers.count > selectedScalerIndex ? scalers[selectedScalerIndex] : Scaler.defaultScalers[selectedScalerIndex]
        }
        set {
            scalers[selectedScalerIndex] = newValue
        }
    }
    
    func Store() {
        
        UserDefaults.standard.set(selectedScalerIndex, forKey: KEY_CURRENTSCALAR)
        
        if let encodedScalers = try? JSONEncoder().encode(Scalers(scalers: scalers)) {
            UserDefaults.standard.set(encodedScalers, forKey: KEY_SCALARS)
            print("SET: KEY_SCALARS:: \(encodedScalers)")
        } else {
            print("FAILED TO STORE: KEY_SCALARS")
        }
    }
    
    func Restore() {
        selectedScalerIndex = UserDefaults.standard.integer(forKey: KEY_CURRENTSCALAR)
        if let storedScalerData = UserDefaults.standard.data(forKey: KEY_SCALARS) {
            if let storedScalers = try? JSONDecoder().decode(Scalers.self, from: storedScalerData) {
            print("RESTORE: KEY_SCALARS")
            scalers = storedScalers.scalers
            } else {
                print("JSONDecoder FAILED TO  RESTORE: KEY_SCALARS")
                scalers = Scaler.defaultScalers
            }
        } else {
            print("UserDefaults FAILED TO RESTORE: KEY_SCALARS")
            scalers = Scaler.defaultScalers
        }
    }
    
    func Clear() {
        scalers = Scaler.defaultScalers
        selectedScalerIndex = 0
        
        UserDefaults.standard.setValue(nil, forKey: KEY_SCALARS)
        UserDefaults.standard.setValue(nil, forKey: KEY_CURRENTSCALAR)
    }
}
