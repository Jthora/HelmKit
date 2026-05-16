//
//  MHDSensorScene.swift
//  HelmKit
//
//  Created by Jordan Trana on 7/21/18.
//  Copyright © 2018 Jordan Trana. All rights reserved.
//

import Foundation
import SceneKit

class MHDSensorScene: SCNScene {
    
    enum SensorSphereType : String {
        case smooth = "sensorSphere_smooth"
        case ripple = "sensorSphere_ripple"
        case smoothChaos = "sensorSphere_smoothChaos"
        case rippleChaos = "sensorSphere_rippleChaos"
        case strongChaos = "sensorSphere_strongChaos"
    }
    
    func sphere(_ sphereType:SensorSphereType) -> SCNNode {
        return self.rootNode.childNode(withName: sphereType.rawValue, recursively: true)!
    }
    
    var mainCamera:SCNNode {
        return self.rootNode.childNode(withName: "mainCamera", recursively: true)!
    }
    
    static func create() -> MHDSensorScene {
        return MHDSensorScene(named: "mhdSensorAssets.scnassets/mhdSensorScene.scn")!
    }
    
}
